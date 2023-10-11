<template>
  <v-layout class="rounded rounded-md">
    <v-app-bar class="px-3" flat density="compact"></v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      @click="rail = false"
    >
      <v-list-item
        prepend-avatar="https://randomuser.me/api/portraits/men/37.jpg"
        title="John Leider"
        nav
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-chevron-left"
            @click.stop="rail = !rail"
          ></v-btn>
        </template>
      </v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          v-for="link in getters.pageMenuItems"
          :key="link.name"
          :to="link.path"
          :value="link.key"
          :title="link.name"
          :prepend-icon="link.icon"
          :active="isActive(link.name)"
        ></v-list-item>

        <v-list-item
          v-if="isLoginAvailable()"
          key="logout"
          value="logout"
          title="Logout"
          prepend-icon="mdi mdi-logout"
          @click="store.dispatch('logout')"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-3">
      <v-progress-linear
        :indeterminate="getters.globalLoading"
        color="blue-lighten-3"
      ></v-progress-linear>
      <v-container>
        <v-row>
          <v-col cols="12" md="9">
            <v-sheet height="90vh" rounded="lg" class="elevation-4">
              <router-view></router-view>
            </v-sheet>
          </v-col>

          <v-col cols="12" md="3">
            <v-sheet rounded="lg" height="90vh" class="elevation-4">
              <v-container>
                <v-card
                  v-for="(action, i) in actions.slice(0, MAX_ACTIONS_LENGTH)"
                  width="100%"
                  density="compact"
                  variant="flat"
                  class="pt-1"
                >
                  <template v-slot:prepend>
                    <v-tooltip activator="parent" location="end"
                      >{{
                        {
                          pending: "pending",
                          completed: "success",
                          faulted: "faulted",
                        }[action.status]
                      }}
                    </v-tooltip>
                    <v-icon
                      size="x-small"
                      :color="ACTION_STATUS_COLOR[action.status]"
                    >
                      {{ ACTION_ICON[action.status] }}
                    </v-icon>
                  </template>
                  <template v-slot:title>
                    <span class="text-caption">{{ action.body }}</span>
                  </template>

                  <template v-slot:subtitle>
                    <span class="text-caption"
                      >station: {{ action.charge_point_id }}</span
                    >
                  </template>
                  <v-divider v-if="i < MAX_ACTIONS_LENGTH - 1"></v-divider>
                </v-card>
              </v-container>
            </v-sheet>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { onMounted, onUnmounted, ref } from "vue";
import store from "@/store";
import { listActions } from "@/services/actions";
import { ACTION_STATUS_COLOR } from "@/components/enums";

const MAX_ACTIONS_LENGTH = 11;

const { currentRoute } = useRouter();
const { getters } = useStore();

var interval = null;
const drawer = ref(true);
const rail = ref(false);
const actions = ref([]);

const ACTION_ICON = {
  pending: "mdi mdi-clock-time-seven-outline",
  completed: "mdi mdi-check",
  faulted: "mdi mdi-cancel",
};

const isLoginAvailable = () => {
  return !currentRoute.value?.meta?.hasBackButton;
};

const isActive = (name) => {
  return currentRoute.value.name === name;
};

onMounted(() => {
  interval = setInterval(() => {
    listActions({ periodic: 1 }).then((response) => (actions.value = response));
  }, 2000);
});

onUnmounted(() => {
  clearInterval(interval);
});
</script>

<style scoped></style>
