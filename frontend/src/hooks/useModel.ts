import { useState } from "react";

import { api } from "../utilities/apiHook";

type SinglePayload = {
    image: File,
    user_query: string
}

type CandidatesPayload = {
    image: File,
    user_query: string,
    candidates: number
}

export type SingleResult =
    | { mineral_name: string; chemical_formula: string }
    | { raw_output: string }; // fallback shape if the model didn't return valid JSON

export type CandidateResult = {
    mineral_name: string;
    chemical_formula: string;
    confidence: number;
};

export function useModel() {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    async function predictSingle(payload: SinglePayload): Promise<SingleResult | undefined> {
        setLoading(true);
        setError(null);
        try {
            // File uploads need multipart form data, not a plain JSON body -
            // a File can't be JSON-serialized. Axios sets the correct
            // multipart Content-Type + boundary automatically when the body
            // is a FormData instance, as long as apiHook.ts isn't forcing a
            // default "Content-Type: application/json" header that would
            // override this - worth checking if uploads still fail.
            const formData = new FormData();
            formData.append("image", payload.image);
            formData.append("user_query", payload.user_query);

            const response = await api.post("/predict/single", formData);
            return response.data as SingleResult;
        } catch (err) {
            console.error(err);
            setError("Couldn't identify that image. Please try again.");
            return undefined;
        } finally {
            setLoading(false);
        }
    }

    async function predictCandidates(payload: CandidatesPayload): Promise<CandidateResult[] | undefined> {
        setLoading(true);
        setError(null);
        try {
            const formData = new FormData();
            formData.append("image", payload.image);
            formData.append("user_query", payload.user_query);
            formData.append("top_k", String(payload.candidates));

            const response = await api.post("/predict/candidates", formData);
            return response.data as CandidateResult[];
        } catch (err) {
            console.error(err);
            setError("Couldn't get predictions. Please try again.");
            return undefined;
        } finally {
            setLoading(false);
        }
    }

    return { loading, error, predictSingle, predictCandidates };
}