
import React, { Component } from 'react';
import { ListGroup, Card } from 'react-bootstrap'

export type SearchResponse = {
    urlId: string,
    summary: string,
    title: string,
    url: string,
    score: number,
    modified_score: number
}

type SearchResultsProps = {
    results: Array<SearchResponse>,
    title: String,
    show_scores: boolean
}

export default class SearchResults extends React.Component<SearchResultsProps> {
    constructor(props: SearchResultsProps) {
        super(props);
        this.formatUrl = this.formatUrl.bind(this);
    }

    private formatUrl(url: String) {
        return url;
        return url.replace("https://starwars.fandom.com/wiki", "");//.replace("%27", "'");
    }

    render() {
        const { results, title, show_scores } = this.props;

        return <div className="container">
            <h1>{title}</h1>
            <ListGroup>
                {results.map(result => (
                    <ListGroup.Item as="li" key={result.urlId}>
                        <Card className="mb-2" >
                            <Card.Body>
                                <Card.Title>{result.title}</Card.Title>
                                <Card.Link href={result.url}>{this.formatUrl(result.url)}</Card.Link>
                                {show_scores ? <Card.Footer><div>Original score: {result.score}<br /> Modified score: {result.modified_score}</div></Card.Footer> : ""}
                            </Card.Body>
                        </Card>
                    </ListGroup.Item>
                ))}
            </ListGroup>
        </div>
    }


}