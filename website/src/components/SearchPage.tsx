import React, { Component } from 'react';
import SearchResults, { SearchResponse } from './SearchResults';
import axios from 'axios';

import { Navbar, Nav, Form, NavDropdown, FormControl, Button, FormCheck, Alert, Spinner } from 'react-bootstrap/'
import { baseUrl } from '../consts';
import { Container, Row, Col } from "react-bootstrap"


let urlPath = baseUrl + "engine/"

type SearchState = {
    value: string,
    keywords: string,
    results: SearchResponse | null,
    show_scores: boolean,
    show_debug: boolean,
    is_debug: boolean,
    temperature: number,
    error: string,
    is_loading: boolean
}

export default class SearchPage extends React.Component<{}, SearchState> {
    constructor(props: Readonly<any>) {
        super(props);
        const isDebug = new URL(window.location.href).searchParams.get('debug') === 'true';
        this.state = { value: '', results: null, show_scores: false, is_debug: isDebug, show_debug: false, keywords: '', temperature: 2.0, error: '', is_loading: false };


        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.onChangeShowScores = this.onChangeShowScores.bind(this);
        this.handleKeywordsChange = this.handleKeywordsChange.bind(this);
        this.onChangeShowDebugInfo = this.onChangeShowDebugInfo.bind(this);
        this.onChangeTemperature = this.onChangeTemperature.bind(this);
    }

    private handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ value: event.target.value });
        this.getSuggestions();
    }
    private onChangeTemperature(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ temperature: Number(event.target.value) });
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
            await this.submitForm();
            this.setState({ results: null, is_loading: true });
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
        const { is_debug, keywords, value, temperature } = this.state;

        axios
            .get<SearchResponse>(urlPath + value, {
                params: {
                    debug: is_debug ? 'true' : 'false',
                    keywords: keywords,
                    temperature: temperature
                }
            })
            .then(response => {
                this.setState({ results: response.data, is_loading: false, error: '' })
            })
            .catch(err => {
                const status = err.response.status;
                const message = err.response.data.message
                if (status == 429) {
                    const displayMessage = 'You are being rate limited. You excideed the following limit: ' + message + '. Please wait and try again.';
                    this.setState({ error: displayMessage });
                }
                else {
                    const displayMessage = 'Unexpected error happened ' + message + ', if you want to please contact Malin with this message.';
                    this.setState({ error: displayMessage });
                }
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

    getForm() {
        const { is_debug, temperature } = this.state;
        return (
            <Form onSubmit={this.handleSubmit}>
                <Row>
                    <Form.Label column sm="1">Keywords</Form.Label>
                    <Col sm="11">
                        <FormControl type="text" placeholder="Comma separated keywords" className="mr-sm-2" value={this.state.keywords} onChange={this.handleKeywordsChange} />
                    </Col>
                </Row>
                <Row>
                    <Form.Label column sm="1">Phrase</Form.Label>
                    <Col md={is_debug ? 9 : 11}>
                        <FormControl required type="text" placeholder="Search phrase" className="mr-sm-2" value={this.state.value} onChange={this.handleChange} />
                        <Button variant="outline-success" type="submit">Search</Button>

                    </Col>
                    {is_debug ? <Form.Label column sm="1">Temp</Form.Label> : ""}
                    {is_debug ? <Col md={1}>

                        <FormControl
                            type="number"
                            step={0.1}
                            value={temperature}
                            onChange={this.onChangeTemperature}
                            className="mr-sm-2"
                        />
                    </Col> : ""}
                </Row>
                <Row>
                    <Col md={1}>Display control:</Col>
                    <Col md={1}>
                        <Form.Check
                            type="checkbox"
                            label="scores"
                            onChange={this.onChangeShowScores}
                        />
                    </Col>
                    {is_debug ?
                        <Col md={9}>
                            <Row>
                                <Col md={2}>
                                    <Form.Check
                                        type="checkbox"
                                        label="debug"
                                        onChange={this.onChangeShowDebugInfo}
                                    />
                                </Col>
                            </Row>
                        </Col> : ""}
                </Row>
            </Form>
        )
    }

    render() {
        const { show_scores, results, show_debug, error, is_loading } = this.state;

        const modifiedScores = results === null ? [] : results.modified_responses;
        const realScores = results === null ? [] : results.original_responses;
        const time = results === null ? 0 : results.time;
        const form = this.getForm();
        return (
            <Container >

                {error != '' ? <Alert key={0} variant='primary'>{error}</Alert> : ""}
                {form}
                {show_debug && time > 0 ? <Row>Found in {time} seconds</Row> : ""}
                {is_loading && !error ? <Spinner animation="border" /> : ""}
                {results !== null ?
                    <Row className="show-grid">

                        <Col xs={2} md={6}>
                            <SearchResults results={realScores} title="Original BM25 results" show_scores={show_scores} is_debug={show_debug} />
                        </Col>
                        <Col xs={2} md={6}>
                            <SearchResults results={modifiedScores} title="Modified results" show_scores={show_scores} is_debug={show_debug} />
                        </Col>
                    </Row> : ""}

            </Container >
        );
    }
}