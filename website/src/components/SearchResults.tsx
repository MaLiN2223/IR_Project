
import React, { Component } from 'react';
import { ListGroup, Card } from 'react-bootstrap'
import '../styles/search_results.css'

export type SearchResponse = {
    original_responses: Array<SearchRecordResponse>
    modified_responses: Array<SearchRecordResponse>
    time: number
}

type DebugInformation = {
    debug_scores: DebugScores
}
type DebugScores = {
    negative_score: number,
    processed_text_similarity: number
}

export type SearchRecordResponse = {
    urlId: string,
    summary: string,
    title: string,
    url: string,
    score: number,
    modified_score: number
    debugInformation: DebugInformation
}

type SearchResultsProps = {
    results: Array<SearchRecordResponse>,
    title: String,
    show_scores: boolean,
    is_debug: boolean
}

export default class SearchResults extends React.Component<SearchResultsProps> {
    constructor(props: SearchResultsProps) {
        super(props);
        this.formatUrl = this.formatUrl.bind(this);
    }

    private formatUrl(url: String) {
        //return url;
        return url.replace("https://starwars.fandom.com/wiki/", "");
    }

    render() {
        const { results, title, show_scores, is_debug } = this.props;

        return <div className="container">
            <h1>{title}</h1>
            <ListGroup>
                {results.map(result => (
                    <ListGroup.Item as="li" key={result.urlId}>
                        <Card>
                            <Card.Body> 
                                <Card.Link href={result.url}>{this.formatUrl(result.url)}</Card.Link> 
                                {show_scores ? <Card.Footer><div>Original score: {result.score}<br /> Modified score: {result.modified_score}</div></Card.Footer> : ""}
                                {is_debug ? <Card.Footer><div>FT smilarity: {result.debugInformation.debug_scores.processed_text_similarity}<br /> Negative BM: {result.debugInformation.debug_scores.negative_score}</div></Card.Footer> : ""}
                            </Card.Body>
                        </Card>
                    </ListGroup.Item>
                ))}
            </ListGroup>
        </div>
    }


}