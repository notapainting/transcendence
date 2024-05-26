import { clearView } from "./index.js";

export const showSettings = async () => {
    clearView();
    const settingsElement = document.querySelector("#settings");

    settingsElement.style.display = "block";
}