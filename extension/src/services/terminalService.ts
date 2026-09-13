import * as vscode from "vscode";


let terminalLogs = "";


const MAX_LOG_SIZE = 50000;


export function startTerminalMonitor(
    context: vscode.ExtensionContext
) {

    const startDisposable =
        vscode.window.onDidStartTerminalShellExecution(
            async event => {

                try {

                    const execution =
                        event.execution;

                    const commandLine =
                        execution.commandLine;

                    terminalLogs +=
                        `\n$ ${commandLine.value}\n`;

                    for await (
                        const data
                        of execution.read()
                    ) {

                        terminalLogs += data;

                        if (
                            terminalLogs.length >
                            MAX_LOG_SIZE
                        ) {

                            terminalLogs =
                                terminalLogs.slice(
                                    -MAX_LOG_SIZE
                                );
                        }
                    }

                } catch (error) {

                    console.error(
                        "Terminal monitoring error:",
                        error
                    );
                }
            }
        );


    const endDisposable =
        vscode.window.onDidEndTerminalShellExecution(
            event => {

                const exitCode =
                    event.exitCode;

                terminalLogs +=
                    `\n[Process exited: ${exitCode ?? "unknown"}]\n`;
            }
        );


    context.subscriptions.push(
        startDisposable,
        endDisposable
    );
}


export function getTerminalLogs(): string {

    return terminalLogs;
}


export function clearTerminalLogs(): void {

    terminalLogs = "";
}