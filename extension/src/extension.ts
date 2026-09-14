import * as vscode from "vscode";
import { startTerminalMonitor } from "./services/terminalService";
import { runDebugCommand } from "./commands/debugCommand";

export function activate(context: vscode.ExtensionContext) {

    startTerminalMonitor(context);

    const debugCommand = vscode.commands.registerCommand(
        "aiProductionDebugger.debug",
        runDebugCommand
    );

    context.subscriptions.push(
        debugCommand
    );
}

export function deactivate() {}