import * as vscode from "vscode";

export function getActiveEditorContext() {

    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        return { activeFile: "", activeCode: ""};
    }

    return {
        activeFile: vscode.workspace.asRelativePath(editor.document.uri),
        activeCode: editor.document.getText(editor.selection) || editor.document.getText()
    };
}