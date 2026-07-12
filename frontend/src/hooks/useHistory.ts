import { useState } from "react";

import { api } from "../utilities/apiHook";
import type { SingleResult, CandidateResult } from "./useModel";

type LogSinglePayload = {
    image_name: string;
    user_query: string;
    result: SingleResult;
};

type LogCandidatesPayload = {
    image_name: string;
    user_query: string;
    results: CandidateResult[];
};

type LogResponse = {
    status: string;
    id: string;
};

export type HistoryEntity = {
    id: string;
    image: string;
    conversations: { from: "human" | "gpt"; value: string }[];
    candidates?: CandidateResult[];
    created_at?: string;
};

export function useHistory() {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    async function logSingle(payload: LogSinglePayload): Promise<LogResponse | undefined> {
        setLoading(true);
        setError(null);
        try {
            // Plain JSON body here, not FormData - there's no file to send,
            // just the filename as a string, and the backend's
            // LogSinglePayload model expects application/json.
            const response = await api.post("/log/single", payload);
            return response.data as LogResponse;
        } catch (err) {
            console.error(err);
            setError("Couldn't save this result to history.");
            return undefined;
        } finally {
            setLoading(false);
        }
    }

    async function logCandidates(payload: LogCandidatesPayload): Promise<LogResponse | undefined> {
        setLoading(true);
        setError(null);
        try {
            const response = await api.post("/log/candidates", payload);
            return response.data as LogResponse;
        } catch (err) {
            console.error(err);
            setError("Couldn't save these results to history.");
            return undefined;
        } finally {
            setLoading(false);
        }
    }

    async function fetchHistory(limit: number = 50): Promise<HistoryEntity[] | undefined> {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get("/log/all", { params: { limit } });
            return response.data as HistoryEntity[];
        } catch (err) {
            console.error(err);
            setError("Couldn't load history.");
            return undefined;
        } finally {
            setLoading(false);
        }
    }

    return { loading, error, logSingle, logCandidates, fetchHistory };
}