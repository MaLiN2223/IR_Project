import React, { Component } from 'react';
import { Link } from 'react-router-dom';

export default class HomePage extends Component<{}> {
    constructor(props: Readonly<{}>) {
        super(props);
    }

    render() {
        return <div>
            <p>
                <h1>Welcome to Malin's page for Web Information Retrieval.</h1>
                <p>Please go to {<Link to="/search">search tab</Link>} to start searching.</p>
                <p>Visit {<Link to="/about">read me tab</Link>} for task description and useful tips</p>
                <p>"Admin" page is only for me, so you will not be able to access anything there</p>
            </p>
        </div>

    }
}