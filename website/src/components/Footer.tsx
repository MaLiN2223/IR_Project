
import axios from 'axios';
import React, { Component } from 'react';
import { baseUrl } from '../consts';


type FooterState = {
    version: string

}

const versionUrl = baseUrl + "metadata/version"

export default class Footer extends React.Component<{}, FooterState> {
    constructor(props: Readonly<any>) {
        super(props);
        this.state = { version: 'unknown' };
    }
    private async refreshVersion(): Promise<boolean> {
        axios
            .get<string>(versionUrl)
            .then(response => {
                this.setState({ version: response.data })
            })
            .catch(x => {
                this.setState({ version: "unable to retrieve the version" })
            })
            ;
        return true;
    }

    componentDidMount() {
        this.refreshVersion()
    }

    render() {
        console.log(`${process.env.REACT_APP_NAME} ${process.env.REACT_APP_CURRENT_GIT_SHA}`)
        return (<footer>
            VERSION: backend {this.state.version} | fontend {process.env.REACT_APP_CURRENT_GIT_SHA}
        </footer>)

    }
}