import AbstractView from './AbstractView.js';

export default class PostsView extends AbstractView {
    constructor(){
        super();
        this.setTitle("Posts");
    }

    async getHtml(){
        return `
            <h1>Posts !!</h1>
        `;
    }
}