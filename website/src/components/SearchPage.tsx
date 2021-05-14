import React, { Component } from 'react';
import SearchResults, { SearchResponse } from './SearchResults';
import axios from 'axios';

import { Navbar, Nav, Form, NavDropdown, FormControl, Button } from 'react-bootstrap/'
import { baseUrl } from '../consts';

let urlPath = baseUrl + "engine/"
let suggestionEndpoint = baseUrl + "suggestion/"

console.log(process.env.NODE_ENV)



interface ISearchQuery {
    q: string;
    debugMode: boolean;
}

type SearchState = {
    value: string,
    results: Array<SearchResponse>,
    submitSuccess: boolean

}

export default class SearchPage extends React.Component<{}, SearchState> {
    constructor(props: Readonly<any>) {
        super(props);
        this.state = { value: '', results: [], submitSuccess: true };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    private handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ value: event.target.value });
        this.getSuggestions();
    }

    private async handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        this.sendForm();
    }

    private async sendForm() {
        if (this.validateForm()) {
            const submitSuccess: boolean = await this.submitForm();
            this.setState({ submitSuccess });
        }
        else {
            // TODO: failue
        }
    }

    private async getSuggestions() {
        if (this.validateSuggestion()) {
            // TODO: call suggestions endpoint
        }

    }
    private validateSuggestion() {
        // TODO:
        return true;
    }

    private validateForm(): boolean {
        // TODO - validate form
        return true;
    }

    private async submitForm(): Promise<boolean> {
        // TODO - submit the form
        console.log("Submitting" + this.state.value)
        axios
            .get<SearchResponse[]>(urlPath + this.state.value, {
                params: {
                    debugMode: 'false',
                    bm25: 'true',
                }
            })
            .then(response => {
                console.log(response)
                this.setState({ results: response.data })
            })
            .catch(x => {
                return false;
            })
            ;
        return true;
    }

    render() {
        return (
            <div>
                <div>
                    <Form inline onSubmit={this.handleSubmit}>
                        <FormControl type="text" placeholder="Search" className="mr-sm-2" value={this.state.value} onChange={this.handleChange} />
                        <Button variant="outline-success" type="submit">Search</Button>
                    </Form>
                    <SearchResults results={this.state.results} /></div>
            </div>
        );
    }
}