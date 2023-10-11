import router from "@/router";
import { request } from "@/api";

const getDefaultState = () => {
  return {
    isAuthorized: false,
    user: {},
  };
};

const state = getDefaultState();

function _processSuccessfulLogout(commit) {
  commit("unsetAuthorized");
  commit("unsetUser");

  router.push("/login");
}

function _processSuccessfulLogin(commit, userData) {
  commit("setAuthorized");
  commit("setUser", userData);

  router.push("/");
}

export default {
  name: "auth",
  state,
  actions: {
    initAction({ getters }, payload) {
      // We don't want to make unnecessary request to the backend in case it's
      // a public page, it may effect Page Load Time
      if (!payload.isPublicPage && getters.isAuthorized) {
        return this.dispatch("getUser").catch(() => {
          console.log("Wasn't able to receive user data");
        });
      } else {
        return Promise.resolve();
      }
    },

    getUser({ commit }) {
      return request.get("/me").then((responseBody) => {
        commit("setUser", responseBody);
      });
    },

    silentLogout({ commit }) {
      _processSuccessfulLogout(commit);
    },

    logout() {
      request.post("/logout");
    },

    login({ commit }, credentials) {
      return request.post("/login", credentials).then((responseBody) => {
        if (responseBody) {
          _processSuccessfulLogin(commit, responseBody);
        } else {
          console.error("Login data is missing");
        }
      });
    },
  },
  getters: {
    isAuthorized(state) {
      return state.isAuthorized;
    },
  },

  mutations: {
    setAuthorized(state) {
      state.isAuthorized = true;
    },

    unsetAuthorized(state) {
      state.isAuthorized = false;
    },

    setUser(state, data) {
      state.user = data;
    },

    unsetUser(state) {
      state.user = {};
    },
  },
};
