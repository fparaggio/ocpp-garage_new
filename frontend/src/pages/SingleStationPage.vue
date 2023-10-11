<template>
  <v-card
    max-width="100%"
    class="text-center elevation-4"
    height="430"
    v-if="station"
  >
    <v-container>
      <v-card-actions>
        <v-row>
          <v-col>
            <v-sheet align="left">
              <v-btn
                :disabled="loading || !isEditAllowed(station)"
                variant="outlined"
                color="blue-darken-1"
                @click="openModal('edit')"
                >Edit
              </v-btn>
            </v-sheet>
          </v-col>
          <v-col>
            <v-sheet align="right">
              <v-btn
                :disabled="loading || !isEditAllowed(station)"
                variant="outlined"
                color="red"
                @click="openConfirm()"
                >Delete
              </v-btn>
            </v-sheet>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-container>
    <v-card-item>
      <v-card-title>
        <v-icon class="mdi mdi-ev-station"></v-icon>
        {{ station.location }}
      </v-card-title>

      <v-card-text class="mb-10">
        <v-chip :color="STATION_STATUS_COLOR[station.status.toLowerCase()]">
          <p class="text-medium-emphasis">
            {{ station.status }}
          </p>
        </v-chip>
        <div>
          <div class="text-h6 mb-1">
            {{ station.vendor }} / {{ station.model }}
          </div>
          <div class="text-overline mb-1">{{ station.id }}</div>
          <div class="text-caption">{{ station.description }}</div>
        </div>
      </v-card-text>
    </v-card-item>
    <v-container>
      <v-card-actions>
        <v-row align="end">
          <v-col></v-col>
          <v-col>
            <v-sheet>
              <v-btn
                :disabled="
                  loading || !isResetAvailable(station) || !progressReset
                "
                variant="outlined"
                color="grey-darken-1"
                @click="resetStation(station.id)"
              >
                <v-progress-circular
                  size="20"
                  color="#0ee018"
                  v-model="progressReset"
                  class="mr-2"
                ></v-progress-circular>
                Reset
              </v-btn>
            </v-sheet>
          </v-col>
          <v-col></v-col>
        </v-row>
      </v-card-actions>
    </v-container>
  </v-card>

  <v-carousel
    v-if="station && station.connectors.length"
    height="400"
    class="mt-3 elevation-4"
    :show-arrows="showArrows()"
    hide-delimiters
  >
    <v-carousel-item v-for="(connector, i) in station.connectors" :key="i">
      <v-card max-width="100%" class="text-center" height="100%">
        <v-card-title primary-title>
          <span class="mdi mdi-connection"></span>
          Connector {{ connector.connector_id }}
        </v-card-title>
        <v-card-subtitle class="mt-10 mb-10">
          <v-chip :color="STATION_STATUS_COLOR[connector.status.toLowerCase()]">
            <p class="text-medium-emphasis">
              {{ connector.status }}
            </p>
          </v-chip>
        </v-card-subtitle>
        <v-chip color="red" v-if="connector.error_code !== 'NoError'">
          <p class="text-medium-emphasis">
            {{ connector.error_code }}
          </p>
        </v-chip>

        <v-container>
          <v-row align="end" style="height: 170px">
            <v-col>
              <v-btn
                :disabled="
                  loading ||
                  connector.status.toLowerCase() !==
                    STATION_STATUS.available.toLowerCase() ||
                  !progressReset
                "
                variant="outlined"
                color="grey-darken-1"
                @click="
                  startRemoteTransaction({
                    charge_point_id: station.id,
                    connector_id: connector.connector_id,
                  })
                "
              >
                <v-progress-circular
                  size="20"
                  color="#0ee018"
                  v-model="progressStart"
                  class="mr-2"
                ></v-progress-circular>
                Start
              </v-btn>
            </v-col>
            <v-col>
              <v-btn
                :disabled="
                  loading ||
                  !isAvailable(station) ||
                  !progressUnlock ||
                  !progressReset
                "
                variant="outlined"
                color="grey-darken-1"
                @click="
                  unlockConnector({
                    stationId: station.id,
                    connectorId: connector.connector_id,
                  })
                "
              >
                <v-progress-circular
                  size="20"
                  color="#0ee018"
                  v-model="progressUnlock"
                  class="mr-2"
                ></v-progress-circular>
                Unlock
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card>
    </v-carousel-item>
  </v-carousel>
  <empty-data v-else></empty-data>

  <empty-data v-if="!station"></empty-data>

  <v-form v-model="isValid">
    <v-container>
      <v-row justify="center">
        <v-dialog v-model="editDialog" persistent width="600">
          <v-card>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      label="Location"
                      :rules="rules.station.locationRules"
                      v-model="data.location"
                      density="compact"
                      variant="underlined"
                      validate-on="lazy blur"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      :rules="rules.station.commentRules"
                      label="Description"
                      v-model="data.description"
                      density="compact"
                      variant="underlined"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
            <v-card-actions class="mb-7">
              <v-spacer></v-spacer>
              <v-btn
                color="blue-darken-1"
                variant="text"
                @click="closeModal('edit')"
                :disabled="loading"
              >
                Close
              </v-btn>
              <v-btn
                color="blue-darken-1"
                variant="text"
                @click="editStation(station.id)"
                :loading="loading"
                :disabled="!isValid"
              >
                Edit
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-row>
    </v-container>
  </v-form>

  <confirm-window :callback="() => removeStation(station.id)"></confirm-window>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { useConfirm } from "@/use/dialogs";

import {
  deleteStation,
  getStation,
  softResetStation,
  updateConnector,
  updateStation,
} from "@/services/stations";
import { remoteStartTransaction } from "@/services/transactions";

import { STATION_STATUS, STATION_STATUS_COLOR } from "@/components/enums";
import { menuItems } from "@/menu/station-menu-items";
import { rules } from "@/configs/validation";
import { watchInterval } from "@/configs";

import EmptyData from "@/components/EmptyData";
import ConfirmWindow from "@/components/dialogs/ConfirmWindow";

var interval = null;
const progressStart = ref(100);
const progressReset = ref(100);
const progressUnlock = ref(100);
const loading = ref(false);
const isValid = ref(false);
const editDialog = ref(false);
const data = ref({});
const errors = ref({});
const showError = ref(false);
const station = ref();
const router = useRouter();
const { commit } = useStore();
const { openConfirm } = useConfirm();

const editStation = (stationId) => {
  loading.value = true;
  updateStation(stationId, data.value)
    .then((response) => {
      station.value = response;
      closeModal("edit");
    })
    .finally(() => {
      loading.value = false;
    });
};

const clearError = () => {
  showError.value = false;
  errors.value = {};
};

const openModal = (type) => {
  if (type === "edit") {
    editDialog.value = true;
  }
};

const closeModal = (type) => {
  if (type === "edit") {
    editDialog.value = false;
    data.value = {};
    clearError();
  }
};

const removeStation = (stationId) => {
  return deleteStation(stationId).then(() => {
    router.push({ name: "Stations" });
  });
};

const showArrows = () => {
  return Object.keys(station.value.connectors).length > 1;
};

const recoverButton = (model) => {
  setTimeout(() => {
    model.value = 100;
  }, watchInterval * 2);
};

const startRemoteTransaction = (data) => {
  loading.value = true;
  remoteStartTransaction(data)
    .then(() => {
      getStation(station.value.id).then(
        (response) => (station.value = response)
      );
    })
    .finally(() => {
      loading.value = false;
      progressStart.value = 0;
      recoverButton(progressStart);
    });
};

const unlockConnector = (data) => {
  loading.value = true;
  updateConnector(data).finally(() => {
    loading.value = false;
    progressUnlock.value = 0;
    recoverButton(progressUnlock);
  });
};

const resetStation = (stationId) => {
  loading.value = true;
  softResetStation(stationId).finally(() => {
    loading.value = false;
    progressReset.value = 0;
    recoverButton(progressReset);
  });
};

const isEditAllowed = (station) => {
  return (
    station.status.toLowerCase() === STATION_STATUS.unavailable.toLowerCase()
  );
};

const isAvailable = (station) => {
  for (let key of Object.keys(station.connectors)) {
    if (
      station.connectors[key].status.toLowerCase() !==
      STATION_STATUS.available.toLowerCase()
    ) {
      return false;
    }
  }
  return true;
};

const isResetAvailable = (station) => {
  if (Object.keys(station.connectors).length > 0) {
    return isAvailable(station);
  } else {
    return false;
  }
};

onMounted(() => {
  commit("setPageMenuItems", menuItems);
  commit("setGlobalLoading");
  getStation(router.currentRoute.value.params.stationId)
    .then((response) => {
      station.value = response;
    })
    .finally(() => {
      commit("unsetGlobalLoading");
    });
  interval = setInterval(() => {
    getStation(router.currentRoute.value.params.stationId).then((response) => {
      station.value = response;
    });
  }, watchInterval);
});

onUnmounted(() => {
  clearInterval(interval);
});
</script>
