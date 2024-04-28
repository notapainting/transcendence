import AbstractView from './AbstractView.js';

export default class SettingsView extends AbstractView {
    constructor(){
        super();
        this.setTitle("Settings");
    }

    async getHtml(){
        return `
            <h1>Settings !!</h1>
        `;
    }
}