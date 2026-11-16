"use strict";

const controls = document.querySelector("[data-controls]");

if (controls) {
  const buttons = Array.from(controls.querySelectorAll("[data-filter]"));
  const search = controls.querySelector("[data-search-input]");
  const rows = Array.from(document.querySelectorAll(".publication[data-topic]"));
  const empty = document.querySelector("[data-empty]");
  const status = document.querySelector("[data-results]");
  let topic = "all";

  function filterPublications() {
    const terms = search.value.toLocaleLowerCase().trim().split(/\s+/u).filter(Boolean);
    let matches = 0;

    for (const row of rows) {
      const inTopic = topic === "all" || row.dataset.topic === topic;
      const haystack = row.dataset.search.toLocaleLowerCase();
      const visible = inTopic && terms.every((term) => haystack.includes(term));
      row.hidden = !visible;
      matches += Number(visible);
    }

    empty.hidden = matches > 0;
    status.textContent = status.dataset.format.replace("{count}", String(matches));
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      topic = button.dataset.filter;
      for (const option of buttons) {
        option.setAttribute("aria-pressed", String(option === button));
      }
      filterPublications();
    });
  }

  search.addEventListener("input", filterPublications);
  controls.hidden = false;
}
