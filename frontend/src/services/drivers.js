import { request } from "@/api";

const endpoint = "drivers";

export function deleteDriver(driverId) {
  return request.delete(`/${endpoint}/${driverId}`);
}

export function addDriver(data) {
  return request.post(`/${endpoint}/`, data);
}

export function listDrivers(params) {
  let searchParams = new URLSearchParams(params);
  return request.get(`/${endpoint}/?${searchParams.toString()}`);
}

export function getDriver(driverId) {
  return request.get(`/${endpoint}/${driverId}`);
}

export function updateDriver(driverId, data) {
  return request.put(`/${endpoint}/${driverId}`, data);
}

export function releaseStation({ driverId, stationId }) {
  return request.delete(`/${endpoint}/${driverId}/charge_points/${stationId}/`);
}
