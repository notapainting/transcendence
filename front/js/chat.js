import { clearView } from "./index.js";

export const showChat = async () => {
    clearView();
    const chatElement = document.querySelector("#chat");
    chatElement.style.display = "block";
}