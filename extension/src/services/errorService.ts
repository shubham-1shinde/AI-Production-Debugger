import {
    getTerminalLogs
} from "./terminalService";


export function getErrorMessage(): string {

    const logs =
        getTerminalLogs();

    if (!logs.trim()) {

        return "";
    }

    return logs;
}