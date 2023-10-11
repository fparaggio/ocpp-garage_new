import { request } from "@/api";

const endpoint = "transactions";

export function listTransactions(params) {
  let searchParams = new URLSearchParams(params);
  return request.get(`/${endpoint}/?${searchParams.toString()}`);
}

export function remoteStartTransaction(data) {
  return request.post(`/${endpoint}/`, data);
}

export function remoteStopTransaction(transactionId) {
  return request.put(`/${endpoint}/${transactionId}`);
}
