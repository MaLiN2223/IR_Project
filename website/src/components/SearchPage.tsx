import React, { Component } from 'react';
import SearchResults, { SearchResponse } from './SearchResults';
import axios from 'axios';

import { Navbar, Nav, Form, NavDropdown, FormControl, Button, FormCheck } from 'react-bootstrap/'
import { baseUrl } from '../consts';
import { Container, Row, Col } from "react-bootstrap"


let urlPath = baseUrl + "engine/"
let suggestionEndpoint = baseUrl + "suggestion/"

console.log(process.env.NODE_ENV)

interface ISearchQuery {
    q: string;
    debugMode: boolean;
}

type SearchState = {
    value: string,
    keywords: string,
    results: Array<SearchResponse>,
    submitSuccess: boolean,
    show_scores: boolean,
    show_debug: boolean,
    is_debug: boolean
}

export default class SearchPage extends React.Component<{}, SearchState> {
    constructor(props: Readonly<any>) {
        super(props);
        const isDebug = new URL(window.location.href).searchParams.get('debug') === 'true';
        this.state = { value: '', results: [], submitSuccess: true, show_scores: false, is_debug: isDebug, show_debug: false, keywords: '' };


        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.onChangeShowScores = this.onChangeShowScores.bind(this);
        this.handleKeywordsChange = this.handleKeywordsChange.bind(this);
        this.onChangeShowDebugInfo = this.onChangeShowDebugInfo.bind(this);
    }

    private handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ value: event.target.value });
        this.getSuggestions();
    }

    private handleKeywordsChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ keywords: event.target.value });
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
        const { is_debug, keywords, value } = this.state;

        axios
            .get<SearchResponse[]>(urlPath + value, {
                params: {
                    debug: is_debug ? 'true' : 'false',
                    bm25: 'true',
                    keywords: keywords
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

    private onChangeShowScores(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ show_scores: event.target.checked });
    }
    private onChangeShowDebugInfo(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ show_debug: event.target.checked });
    }

    render() {
        const { show_scores, results, is_debug } = this.state;
        const modifiedScores = [...results].sort((n1: SearchResponse, n2: SearchResponse) => (n2.modified_score - n1.modified_score))//.slice(0, 10);
        console.log(modifiedScores.length)
        const realScores = [...results].sort((n1: SearchResponse, n2: SearchResponse) => (n2.score - n1.score))//.slice(0, 10);

        return (
            <Container >

                <Form onSubmit={this.handleSubmit}>
                    <Row>
                        <Form.Label column sm="1">Keywords</Form.Label>
                        <Col sm="11">
                            <FormControl type="text" placeholder="Comma separated keywords" className="mr-sm-2" value={this.state.keywords} onChange={this.handleKeywordsChange} />
                        </Col>
                    </Row>
                    <Row>
                        <Form.Label column sm="1">Search phrase</Form.Label>
                        <Col md={is_debug ? 9 : 10}>
                            <FormControl type="text" placeholder="Search phrase" className="mr-sm-2" value={this.state.value} onChange={this.handleChange} />
                            <Button variant="outline-success" type="submit">Search</Button>

                        </Col>
                        <Col md={1}>
                            <Form.Check
                                type="checkbox"
                                label="Show scores"
                                onChange={this.onChangeShowScores}
                            />
                        </Col>
                        {is_debug ?
                            <Col md={1}>
                                <Form.Check
                                    type="checkbox"
                                    label="Show debug info"
                                    onChange={this.onChangeShowDebugInfo}
                                />
                            </Col> : ""}
                    </Row>
                </Form>
                <Row className="show-grid">
                    <Col xs={2} md={6}>
                        <SearchResults results={realScores} title="Original BM25 results" show_scores={show_scores} />
                    </Col>
                    <Col xs={2} md={6}>
                        <SearchResults results={modifiedScores} title="Modified results" show_scores={show_scores} />
                    </Col>
                </Row>

            </Container >
        );
    }
}