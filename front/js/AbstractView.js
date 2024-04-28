
export default class AbstractView {
    constructor(){

    }
    setTitle(title) {
        document.title = title;
    }

    async getHtml() {
        return "";
    }
}