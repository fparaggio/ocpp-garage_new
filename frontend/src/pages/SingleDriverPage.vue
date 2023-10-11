<template>
  <v-card
    max-width="100%"
    class="text-center elevation-4"
    height="330"
    v-if="driver"
  >
    <v-container>
      <v-card-actions>
        <v-row>
          <v-col>
            <v-sheet align="left">
              <v-btn
                :active="!loading"
                variant="outlined"
                :color="driver.is_active ? 'blue-darken-1' : 'red'"
                @click="manageDriver()"
                >{{ driver.is_active ? "Block" : "Recover" }}
              </v-btn>
            </v-sheet>
          </v-col>
          <v-col>
            <v-sheet align="right">
              <v-btn variant="outlined" color="red" @click="openConfirm()"
                >Delete
              </v-btn>
            </v-sheet>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-container>
    <v-card-item>
      <v-card-title>
        <v-icon class="mdi mdi-account-circle"></v-icon>
        {{ driver.first_name }} {{ driver.last_name }}
      </v-card-title>

      <v-card-text class="mt-10">
        <v-chip :color="DRIVERS_STATUS[driver.is_active]">
          <p class="text-medium-emphasis">
            {{ driver.is_active ? "Active" : "Blocked" }}
          </p>
        </v-chip>
        <div>
          <div class="text-h6 mt-10">
            {{ driver.address }}
          </div>
        </div>
      </v-card-text>
    </v-card-item>
  </v-card>
  <v-card
    max-width="100%"
    class="text-center mt-3 elevation-4"
    height="500"
    v-if="driver"
  >
    <data-table
      :hover="false"
      :paginate="false"
      title="Stations"
      :items="driver.charge_points"
      :headers="headers"
    >
      <template v-slot:title="{ title }">
        <v-row>
          <v-col></v-col>
          <v-col class="d-flex justify-center mb-6">
            <v-card-item>{{ title }}</v-card-item>
          </v-col>
          <v-col class="d-flex justify-end mb-6 mt-3">
            <v-btn color="blue-lighten-1" class="ma-6 pa-2" @click="openModal"
              >add
            </v-btn>
          </v-col>
        </v-row>
      </template>
      <template v-slot:item.status="{ item }">
        <v-chip
          :color="STATION_STATUS_COLOR[item.columns.status.toLowerCase()]"
        >
          <p class="text-medium-emphasis">
            {{ item.columns.status }}
          </p>
        </v-chip>
      </template>
      <template v-slot:item.action="{ item }">
        <v-hover v-slot="{ isHovering, props }" open-delay="100">
          <v-btn
            icon
            size="small"
            density="compact"
            :elevation="isHovering ? 12 : 2"
            :class="{ 'on-hover': isHovering }"
            :loading="loading"
            :disabled="loading"
            v-bind="props"
            @click="unbindStation(item)"
          >
            <v-icon color="deep-orange-lighten-3">mdi-trash-can-outline</v-icon>
          </v-btn>
        </v-hover>
      </template>
    </data-table>
  </v-card>
  <v-form>
    <v-container>
      <v-row justify="center">
        <v-dialog v-model="dialog" persistent width="400">
          <v-card>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col cols="12" class="mt-7">
                    <v-autocomplete
                      :items="stations"
                      v-model="data.charge_point_id"
                      required
                      label="Station"
                      density="compact"
                      variant="underlined"
                      item-title="location"
                      item-value="id"
                    ></v-autocomplete>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
            <v-card-actions class="mb-7">
              <v-spacer></v-spacer>
              <v-btn
                color="blue-darken-1"
                variant="text"
                @click="closeModal"
                :disabled="loading"
              >
                Close
              </v-btn>
              <v-btn
                color="blue-darken-1"
                variant="text"
                @click="bindStation"
                :loading="loading"
                :disabled="!data.charge_point_id || loading"
              >
                Add
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-row>
    </v-container>
  </v-form>
  <confirm-window :callback="() => removeDriver(driver.id)"></confirm-window>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { useConfirm } from "@/use/dialogs";

import {
  deleteDriver,
  getDriver,
  releaseStation,
  updateDriver,
} from "@/services/drivers";
import { listSimpleStations } from "@/services/stations";
import { menuItems } from "@/menu/driver-menu-items";
import { DRIVERS_STATUS, STATION_STATUS_COLOR } from "@/components/enums";
import ConfirmWindow from "@/components/dialogs/ConfirmWindow";
import DataTable from "@/components/DataTable";
import { dateAgo } from "@/filters/date";

const data = ref({});
const stations = ref([]);
const dialog = ref(false);
const loading = ref(false);
const driver = ref();
const router = useRouter();
const { commit } = useStore();
const { openConfirm } = useConfirm();

const openModal = () => {
  listSimpleStations().then((response) => {
    dialog.value = true;
    stations.value = response;
  });
};

const closeModal = () => {
  dialog.value = false;
  data.value = {};
};

const manageDriver = () => {
  loading.value = true;
  updateDriver(driver.value.id, { is_active: !driver.value.is_active })
    .then((response) => {
      driver.value = response;
    })
    .finally(() => {
      loading.value = false;
    });
};

const bindStation = () => {
  loading.value = true;
  updateDriver(driver.value.id, { charge_point_id: data.value.charge_point_id })
    .then((response) => {
      driver.value = response;
    })
    .finally(() => {
      loading.value = false;
      closeModal();
    });
};

const unbindStation = (item) => {
  loading.value = true;
  releaseStation({ driverId: driver.value.id, stationId: item.columns.id })
    .then(() => {
      console.log(driver.value);
      driver.value.charge_points = driver.value.charge_points.filter(
        (i) => i.id !== item.columns.id
      );
    })
    .finally(() => {
      loading.value = false;
    });
};

const removeDriver = (driverId) => {
  return deleteDriver(driverId).then(() => {
    router.push({ name: "Drivers" });
  });
};

onMounted(() => {
  commit("setPageMenuItems", menuItems);
  commit("setGlobalLoading");
  getDriver(router.currentRoute.value.params.driverId)
    .then((response) => {
      driver.value = response;
    })
    .finally(() => {
      commit("unsetGlobalLoading");
    });
});

const headers = [
  {
    title: "Id",
    key: "id",
    align: "center",
    sortable: false,
    width: "25%",
  },
  {
    title: "Status",
    key: "status",
    align: "center",
    sortable: false,
    width: "20%",
  },
  {
    title: "Location",
    key: "location",
    align: "center",
    sortable: false,
    width: "20%",
  },
  {
    title: "Last activity",
    key: "updated_at",
    align: "center",
    sortable: true,
    value: (v) => dateAgo(v.updated_at),
    width: "20%",
  },
  {
    title: "",
    align: "left",
    width: "8%",
    sortable: false,
    key: "action",
  },
];
</script>
