export interface DebugRequest {

    repo: string;

    branch: string;

    errorMessage: string;

    terminalLogs: string;

    workspacePath: string;

    activeFile: string;

    activeCode: string;

    diagnostics: any[];
}


export interface DebugResponse {

    success: boolean;

    answer?: string;

    index?: any;

    detail?: string;
}


const BACKEND_URL =
    "http://127.0.0.1:8000";


export async function sendDebugRequest(
    request: DebugRequest
): Promise<DebugResponse> {

    const response =
        await fetch(
            `${BACKEND_URL}/api/debug`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(request)
            }
        );


    const data = await response.json();

    console.log(data)


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Backend debugging request failed."
        );
    }


    return data;
}