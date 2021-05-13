
import React, { Component } from 'react';
import { ListGroup } from 'react-bootstrap'

export type SearchResponse = {
    urlId: string,
    summary: string,
    title: string,
    url: string,
}

type SearchResultsProps = {
    results: Array<SearchResponse>
}

export default class SearchResults extends React.Component<SearchResultsProps> {
    constructor(props: SearchResultsProps) {
        super(props);
    }

    render() {
        const { results } = this.props;
        return <div className="container">  
            <div>Results:</div>

            <ListGroup>

                {results.map(result => (
                    <ListGroup.Item as="li">
                        <a href={result.url}>{result.title} | {result.url}</a>
                        <div>
                            {result.summary}
                        </div>
                    </ListGroup.Item>
                ))}
            </ListGroup>
        </div>
    }


}