import * as vscode from "vscode";

import {
    getWorkspaceInfo
} from "../services/workspaceService";

import {
    getActiveEditorContext
} from "../services/editorService";

import {
    getDiagnostics
} from "../services/diagnosticService";

import {
    getTerminalLogs
} from "../services/terminalService";

import {
    sendDebugRequest
} from "../services/backendService";


export async function runDebugCommand() {

    try {

        await vscode.window.withProgress(
            {
                location:
                    vscode.ProgressLocation.Notification,

                title:
                    "AI Production Debugger",

                cancellable: false
            },

            async progress => {

                progress.report({
                    message:
                        "Collecting debugging context..."
                });


                // -----------------------------
                // WORKSPACE
                // -----------------------------

                const workspace =
                    await getWorkspaceInfo();


                // -----------------------------
                // EDITOR
                // -----------------------------

                const editor =
                    getActiveEditorContext();


                // -----------------------------
                // DIAGNOSTICS
                // -----------------------------

                const diagnostics =
                    getDiagnostics();


                // -----------------------------
                // TERMINAL
                // -----------------------------

                const terminalLogs =
                    getTerminalLogs();


                if (!terminalLogs.trim()) {

                    vscode.window.showWarningMessage(
                        "No terminal output captured yet."
                    );
                }


                // -----------------------------
                // ERROR
                // -----------------------------

                const errorMessage =
                    terminalLogs;


                // -----------------------------
                // REQUEST
                // -----------------------------

                progress.report({
                    message:
                        "Sending data to AI debugger..."
                });


                const result =
                    await sendDebugRequest({

                        repo:
                            workspace.repo,

                        branch:
                            workspace.branch,

                        errorMessage,

                        terminalLogs,

                        workspacePath:
                            workspace.workspacePath,

                        activeFile:
                            editor.activeFile,

                        activeCode:
                            editor.activeCode,

                        diagnostics
                    });


                // -----------------------------
                // SHOW RESULT
                // -----------------------------

                progress.report({
                    message:
                        "Debug analysis completed."
                });


                if (!result.success) {

                    throw new Error(
                        result.detail ||
                        "Debugger failed."
                    );
                }


                showDebugResult(
                    result.answer || ""
                );
            }
        );

    } catch (error) {

        const message =
            error instanceof Error
                ? error.message
                : String(error);

        vscode.window.showErrorMessage(
            `AI Debugger: ${message}`
        );
    }
}


function showDebugResult(
    answer: string
) {

    const panel =
        vscode.window.createWebviewPanel(
            "aiDebuggerResult",
            "AI Debugger",
            vscode.ViewColumn.Beside,
            {
                enableScripts: false
            }
        );


    panel.webview.html = `
        <!DOCTYPE html>

        <html>

        <head>

            <meta
                charset="UTF-8"
            />

            <style>

                body {
                    padding: 24px;
                    font-family:
                        var(
                            --vscode-font-family
                        );
                    color:
                        var(
                            --vscode-foreground
                        );
                    background:
                        var(
                            --vscode-editor-background
                        );
                }

                pre {
                    white-space:
                        pre-wrap;
                    word-wrap:
                        break-word;
                }

            </style>

        </head>

        <body>

            <h1>
                AI Production Debugger
            </h1>

            <pre>
${escapeHtml(answer)}
            </pre>

        </body>

        </html>
    `;
}


function escapeHtml(
    text: string
): string {

    return text
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}