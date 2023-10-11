// Composables
import { createRouter, createWebHistory } from "vue-router";
import AuthGuard from "./guards/auth-guard";
import PublicPageGuard from "./guards/public-page-guard";

const routes = [
  {
    path: "/login",
    name: "login",
    beforeEnter: PublicPageGuard,
    component: () =>
      import(/* webpackChunkName: "home" */ "@/pages/LoginPage.vue"),
    meta: {
      public: true,
    },
  },
  {
    path: "/",
    component: () => import("@/layouts/AppLayout.vue"),
    beforeEnter: AuthGuard,
    children: [
      {
        path: "",
        name: "Dashboard",
        component: () =>
          import(/* webpackChunkName: "home" */ "@/pages/DashboardPage"),
      },
      {
        path: "stations",
        name: "Stations",
        component: () =>
          import(/* webpackChunkName: "home" */ "@/pages/StationsPage.vue"),
      },
      {
        path: "stations/:stationId",
        name: "SingleStation",
        component: () =>
          import(
            /* webpackChunkName: "home" */ "@/pages/SingleStationPage.vue"
          ),
        meta: {
          hasBackButton: true,
        },
      },
      {
        path: "drivers",
        name: "Drivers",
        component: () =>
          import(/* webpackChunkName: "home" */ "@/pages/DriversPage"),
      },
      {
        path: "drivers/:driverId",
        name: "SingleDriver",
        component: () =>
          import(/* webpackChunkName: "home" */ "@/pages/SingleDriverPage.vue"),
        meta: {
          hasBackButton: true,
        },
      },
      {
        path: "transactions",
        name: "Transactions",
        component: () =>
          import(/* webpackChunkName: "home" */ "@/pages/TransactionsPage"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
