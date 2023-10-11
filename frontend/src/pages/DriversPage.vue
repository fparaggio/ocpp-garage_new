<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="12">
        <v-sheet height="80vh">
          <data-table
            title="Drivers"
            :items="items"
            :headers="headers"
            :current-page="currentPage"
            :last-page="lastPage"
            @page-updated="(newPage) => (currentPage = newPage)"
            @click-row="onClickRow"
          >
            <template v-slot:title="{ title }">
              <v-row>
                <v-col md="5">
                  <v-card-item class="ma-6 pa-2" width="100%">
                    <v-text-field
                      label="Email, Name or Address"
                      density="compact"
                      variant="outlined"
                      append-inner-icon="mdi-magnify"
                      v-model="search"
                    >
                    </v-text-field>
                  </v-card-item>
                </v-col>
                <v-col class="d-flex justify-left mb-6">
                  <v-card-item>{{ title }}</v-card-item>
                </v-col>
                <v-col class="d-flex justify-end mb-6 mt-3">
                  <v-btn
                    color="blue-lighten-1"
                    class="ma-6 pa-2"
                    @click="openModal"
                    >add
                  </v-btn>
                </v-col>
              </v-row>
            </template>
            <template v-slot:item.is_active="{ item }">
              <v-chip :color="DRIVERS_STATUS[item.columns.is_active]">
                <p class="text-medium-emphasis">
                  {{ item.columns.is_active ? "Active" : "Blocked" }}
                </p>
              </v-chip>
            </template>
          </data-table>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
  <v-form v-model="isValid">
    <v-container>
      <v-row justify="center">
        <v-dialog v-model="dialog" persistent width="600">
          <v-card>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      :error="showError && errors.id"
                      :error-messages="errors.email"
                      :rules="rules.driver.emailRules"
                      label="E-mail"
                      required
                      v-model="data.email"
                      density="compact"
                      variant="underlined"
                      validate-on="lazy blur"
                      @input="clearError"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      label="First Name"
                      :rules="rules.driver.firstNameRules"
                      v-model="data.first_name"
                      density="compact"
                      variant="underlined"
                      validate-on="lazy blur"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      :rules="rules.driver.lastNameRules"
                      label="Last Name"
                      required
                      v-model="data.last_name"
                      density="compact"
                      variant="underlined"
                      validate-on="lazy blur"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      :rules="rules.driver.addressRules"
                      label="Address"
                      required
                      v-model="data.address"
                      density="compact"
                      variant="underlined"
                      @input="clearError"
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
                @click="closeModal"
                :disabled="loading"
              >
                Close
              </v-btn>
              <v-btn
                color="blue-darken-1"
                variant="text"
                @click="sendData"
                :loading="loading"
                :disabled="!isValid || loading"
              >
                Add
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useStore } from "vuex";
import DataTable from "@/components/DataTable";
import router from "@/router";
import { rules } from "@/configs/validation";

import { DRIVERS_STATUS } from "@/components/enums";
import { usePagination } from "@/use/pagination";
import { addDriver, listDrivers } from "@/services/drivers";
import { menuItems } from "@/menu/app-menu-items";

const loading = ref(false);
const isValid = ref(false);
const dialog = ref(false);
const data = ref({});
const errors = ref({});
const showError = ref(false);

const { currentPage, lastPage, fetchData, items, search } = usePagination({
  itemsLoader: listDrivers,
});

const onClickRow = ({ item }) => {
  router.push({
    name: "SingleDriver",
    params: { driverId: item.key },
  });
};

const clearError = () => {
  showError.value = false;
  errors.value = {};
};

const openModal = () => {
  dialog.value = true;
};

const closeModal = () => {
  dialog.value = false;
  data.value = {};
  clearError();
};

const sendData = () => {
  loading.value = true;
  addDriver(data.value)
    .then(() => {
      fetchData();
      loading.value = false;
      closeModal();
    })
    .catch(({ response }) => {
      const { data } = response;
      showError.value = true;
      errors.value[data.key] = data.detail;
      loading.value = false;
    });
};

onMounted(() => {
  const { commit } = useStore();
  commit("setPageMenuItems", menuItems);
});

const headers = [
  {
    title: "E-mail",
    key: "email",
    align: "right",
    sortable: false,
    width: "30%",
  },
  {
    title: "Name",
    key: "first_name",
    align: "center",
    sortable: false,
    value: (v) => `${v.first_name} ${v.last_name}`,
    width: "20%",
  },
  {
    title: "Address",
    key: "address",
    align: "center",
    sortable: true,
    width: "40%",
  },
  {
    title: "Status",
    align: "center",
    width: "15%",
    sortable: false,
    key: "is_active",
  },
];
</script>
