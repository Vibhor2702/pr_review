"""Main CLI entrypoint for the PR review agent."""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from src.config import config
from src.utils import setup_logging, ensure_artifacts_dir
from src.fetch_prs import get_fetcher
from src.repo_checkout import RepoCheckout
from src.analyze_code import analyze_code
from src.review_generator import generate_review
from src.scoring import calculate_pr_score
from src.ci_integration import save_review_artifacts
from src.providers.gemini_provider import GeminiProvider

console = Console()


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Automated Pull Request Review Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s review --provider github --owner microsoft --repo vscode --pr 123
  %(prog)s serve --host 0.0.0.0 --port 5000
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Review command
    review_parser = subparsers.add_parser("review", help="Review a PR")
    review_parser.add_argument("--provider", required=True, choices=["github", "gitlab", "bitbucket"], help="Git provider")
    review_parser.add_argument("--owner", required=True, help="Repository owner")
    review_parser.add_argument("--repo", required=True, help="Repository name")
    review_parser.add_argument("--pr", type=int, required=True, help="PR number")
    review_parser.add_argument("--token", help="Override auth token")
    review_parser.add_argument("--output", default="artifacts", help="Output directory for artifacts")
    review_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    review_parser.add_argument("--no-llm", action="store_true", help="Skip LLM analysis")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start HTTP server")
    serve_parser.add_argument("--host", default=config.server_host, help="Server host")
    serve_parser.add_argument("--port", type=int, default=config.server_port, help="Server port")
    serve_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    if args.command == "review":
        return run_review(args)
    elif args.command == "serve":
        return run_server(args)
    
    return 0


def run_review(args) -> int:
    """Run PR review command."""
    console.print(Panel.fit("PR Review Agent", style="bold blue"))
    
    try:
        # Validate configuration
        missing_config = config.validate_required_config([args.provider])
        if args.no_llm:
            # Remove Gemini key from required if LLM is disabled
            missing_config = [c for c in missing_config if c != "GEMINI_API_KEY"]
        
        if missing_config:
            console.print(f"❌ Missing configuration: {', '.join(missing_config)}", style="bold red")
            console.print("Please check your .env file or environment variables.")
            return 1
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Fetch PR information
            task1 = progress.add_task("Fetching PR information...", total=None)
            fetcher = get_fetcher(args.provider, args.token)
            pr_context = fetcher.get_pr_info(args.owner, args.repo, args.pr)
            progress.update(task1, completed=True)
            
            # Display PR info
            console.print(f"\n📋 PR #{pr_context['pr_number']}: {pr_context['title']}")
            console.print(f"🌿 {pr_context['head_ref']} → {pr_context['base_ref']}")
            console.print(f"📁 {len(pr_context['files'])} files changed")
            
            # Checkout repository
            task2 = progress.add_task("Checking out repository...", total=None)
            checkout_manager = RepoCheckout()
            repo_path = checkout_manager.checkout_pr(
                pr_context['repo_url'],
                pr_context['head_ref'],
                pr_context['base_ref']
            )
            progress.update(task2, completed=True)
            
            # Analyze code
            task3 = progress.add_task("Analyzing code...", total=None)
            changed_files = [f['path'] for f in pr_context['files']]
            
            llm_provider = None if args.no_llm else GeminiProvider()
            findings = analyze_code(repo_path, changed_files, pr_context, llm_provider)
            progress.update(task3, completed=True)
            
            # Generate review
            task4 = progress.add_task("Generating review...", total=None)
            review_data = generate_review(findings, pr_context)
            score_data = calculate_pr_score(findings, pr_context)
            review_data["score"] = score_data
            progress.update(task4, completed=True)
            
            # Save artifacts
            task5 = progress.add_task("Saving artifacts...", total=None)
            ensure_artifacts_dir()
            artifact_path = save_review_artifacts(review_data, pr_context, args.output)
            progress.update(task5, completed=True)
            
            # Clean up
            checkout_manager.cleanup(repo_path)
        
        # Display results
        display_review_results(review_data, artifact_path)
        
        # Return exit code based on score
        score = score_data.get("score", 0)
        if score < 60:
            return 2  # Significant issues
        elif score < 80:
            return 1  # Minor issues
        else:
            return 0  # Good quality
            
    except KeyboardInterrupt:
        console.print("\n❌ Review interrupted by user", style="bold yellow")
        return 130
    except Exception as e:
        console.print(f"❌ Review failed: {str(e)}", style="bold red")
        logging.error(f"Review failed: {e}", exc_info=True)
        return 1


def display_review_results(review_data: dict, artifact_path: str):
    """Display review results in the console."""
    score_data = review_data.get("score", {})
    comments = review_data.get("comments", [])
    
    # Score panel
    score = score_data.get("score", 0)
    grade = score_data.get("grade", "F")
    
    score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
    score_panel = Panel(
        f"Score: {score}/100 ({grade})",
        title="📊 PR Quality Score",
        style=score_color
    )
    console.print(score_panel)
    
    # Summary
    console.print(f"\n📝 {review_data.get('summary', 'No summary available')}")
    
    # Metrics table
    metrics = score_data.get("metrics", {})
    if metrics:
        table = Table(title="📈 Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files Changed", str(metrics.get("files_changed", 0)))
        table.add_row("Lines Added", str(metrics.get("lines_added", 0)))
        table.add_row("Lines Removed", str(metrics.get("lines_removed", 0)))
        table.add_row("Total Findings", str(metrics.get("total_findings", 0)))
        table.add_row("Errors", str(metrics.get("error_count", 0)))
        table.add_row("Warnings", str(metrics.get("warning_count", 0)))
        table.add_row("Suggestions", str(metrics.get("info_count", 0)))
        
        console.print(table)
    
    # Recommendations
    recommendations = score_data.get("recommendations", [])
    if recommendations:
        console.print("\n💡 Recommendations:")
        for rec in recommendations:
            console.print(f"  • {rec}")
    
    # Sample findings
    if comments:
        console.print(f"\n🔍 Found {len(comments)} issues. Sample findings:")
        
        for i, comment in enumerate(comments[:3]):  # Show first 3
            severity_style = {
                "error": "bold red",
                "warning": "bold yellow",
                "info": "bold blue"
            }.get(comment.get("severity", "info"), "white")
            
            console.print(f"\n  📄 {comment['file']}:{comment['line']}")
            console.print(f"     {comment['message']}", style=severity_style)
            
            if comment.get("suggestion"):
                console.print(f"     💡 {comment['suggestion']}", style="dim")
    
    console.print(f"\n📁 Full report saved to: {artifact_path}")


def run_server(args) -> int:
    """Run HTTP server."""
    try:
        from src.server import create_app
        app = create_app()
        
        console.print(Panel.fit(f"🚀 Starting server on {args.host}:{args.port}", style="bold green"))
        app.run(host=args.host, port=args.port, debug=args.verbose)
        return 0
    except ImportError:
        console.print("❌ Flask not available for server mode", style="bold red")
        return 1
    except Exception as e:
        console.print(f"❌ Server failed: {str(e)}", style="bold red")
        return 1


if __name__ == "__main__":
    sys.exit(main())