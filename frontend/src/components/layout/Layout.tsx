import React from "react";

export const Layout = ({ children }: { children: React.ReactNode }) => {
  return <div className="container mx-auto px-4">{children}</div>;
};
