import express, { type Express } from "express";
import fs from "fs";
import path from "path";

// Get the server directory - compatible with both ESM and CommonJS
const projectRoot = process.cwd();
const currentDirPath = path.join(projectRoot, 'server');

export function serveStatic(app: Express) {
  const distPath = path.resolve(currentDirPath, "public");
  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`,
    );
  }

  app.use(express.static(distPath));

  // fall through to index.html if the file doesn't exist
  app.use("*", (_req, res) => {
    res.sendFile(path.resolve(distPath, "index.html"));
  });
}
