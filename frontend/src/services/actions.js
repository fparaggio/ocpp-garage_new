import { request } from "@/api";

const endpoint = "actions";

export function listActions(params) {
  let searchParams = new URLSearchParams(params);
  return request.get(`/${endpoint}/?${searchParams.toString()}`);
}
