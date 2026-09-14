import * as vscode from "vscode";

export function getDiagnostics() {

    const diagnostics: any[] = [];

    for (const [uri, collection] of vscode.languages.getDiagnostics()) {

        const file = vscode.workspace.asRelativePath(uri);

        for (const diagnostic of collection) {
            diagnostics.push({
                file,
                message: diagnostic.message,
                severity:
                    diagnostic.severity ===
                    vscode.DiagnosticSeverity.Error
                        ? "Error"
                        : diagnostic.severity ===
                          vscode.DiagnosticSeverity.Warning
                            ? "Warning"
                            : "Info",
                line: diagnostic.range.start.line + 1,
                column: diagnostic.range.start.character + 1
            });
        }
    }
    return diagnostics;
}