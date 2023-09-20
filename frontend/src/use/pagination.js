import { watch, ref } from "vue";
import { useStore } from "vuex";
import { rules } from "@/configs/validation";

export function usePagination({ itemsLoader }) {
  const currentPage = ref(1);
  const lastPage = ref(0);
  const items = ref([]);
  const search = ref("");
  const { commit } = useStore();
  let timeout = null;

  const fetchData = () => {
    commit("setGlobalLoading");
    itemsLoader({ page: currentPage.value, search: search.value }).then(
      (response) => {
        if (!response.items.length && currentPage.value > 1) {
          currentPage.value--;
        }
        items.value = response.items;
        lastPage.value = response.pagination.last_page;
        commit("unsetGlobalLoading");
      }
    );
  };
  fetchData();
  watch(currentPage, () => fetchData());
  watch(search, (newValue, oldValue) => {
    let newValueLength = newValue.trim().length;
    let oldValueLength = oldValue.trim().length;
    if (
      newValueLength >= rules.minLength ||
      (!newValueLength && oldValueLength)
    ) {
      clearTimeout(timeout);
      timeout = setTimeout(fetchData, 500, newValue);
    }
  });
  return { currentPage, lastPage, fetchData, items, search };
}