import React, { Component } from 'react';
import axios from 'axios';

let urlPath = "http://127.0.0.1:5000/engine/"

interface ISearchQuery {
    q: string;
}

const defaultQuery: ISearchQuery[] = [];


export default class SearchPage extends React.Component<{}, { [key: string]: string }> {
    constructor(props: Readonly<{}>) {
        super(props);
        this.state = { value: '' };

        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    private handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState({ value: event.target.value });
    }

    private async handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();
        if (this.validateForm()) {
            const submitSuccess: boolean = await this.submitForm();
            //this.setState({ submitSuccess });
        }
    }
    private validateForm(): boolean {
        // TODO - validate form
        return true;
    }

    private async submitForm(): Promise<boolean> {
        // TODO - submit the form
        console.log("Submitting" + this.state.value)
        axios
            .get<ISearchQuery[]>(urlPath + this.state.value)
            .then(response => {
                console.log(response)
            })
            ;
        return true;
    }

    render() {
        return (
            <div>
                <div className='main-content'>
                    {/* <Typography>{this.state.searchItem}</Typography> */}
                    <form onSubmit={this.handleSubmit} noValidate={true}>
                        <label>
                            Name:
                            <input type="text" value={this.state.value} onChange={this.handleChange} />
                        </label>
                        <input type="submit" value="Submit" />
                    </form>
                </div>
            </div>
        );
    }
}