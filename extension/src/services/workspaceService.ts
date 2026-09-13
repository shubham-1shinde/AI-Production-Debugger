import * as vscode from "vscode";
import { execFile } from "child_process";

function execGit(
    args: string[],
    cwd: string
): Promise<string> {

    return new Promise((resolve, reject) => {

        execFile(
            "git",
            args,
            {
                cwd,
                windowsHide: true
            },
            (error, stdout, stderr) => {

                if (error) {
                    reject(
                        new Error(
                            stderr || error.message
                        )
                    );

                    return;
                }

                resolve(stdout.trim());
            }
        );
    });
}


export async function getWorkspaceInfo() {

    const workspace =
        vscode.workspace.workspaceFolders?.[0];

    if (!workspace) {
        throw new Error(
            "No VS Code workspace is open."
        );
    }

    const workspacePath =
        workspace.uri.fsPath;

    const repoUrl =
        await execGit(
            ["config", "--get", "remote.origin.url"],
            workspacePath
        );

    const branch =
        await execGit(
            ["branch", "--show-current"],
            workspacePath
        );

    let repo = repoUrl;

    if (repo.startsWith("git@github.com:")) {

        repo = repo.replace(
            "git@github.com:",
            ""
        );

    } else if (repo.includes("github.com/")) {

        repo =
            repo.split("github.com/")[1];
    }

    repo = repo.replace(
        /\.git$/,
        ""
    );

    return {
        workspacePath,
        repo,
        branch
    };
}