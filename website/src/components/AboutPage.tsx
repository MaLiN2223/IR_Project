import React, { Component } from 'react';
import { Accordion, Button, Card } from 'react-bootstrap';
import "../styles/about.css"

type ExpandableProps = {
    key: string,
    titleText: string,
    bodyText: string
}


const createCard: any = (key: string, title: string, body: any) => <Card>
    <Accordion.Toggle as={Card.Header} eventKey={key}>
        {title}
    </Accordion.Toggle>
    <Accordion.Collapse eventKey={key}>
        <Card.Body>{body}</Card.Body>
    </Accordion.Collapse>
</Card>
export default class AboutPage extends Component<{}> {
    constructor(props: Readonly<{}>) {
        super(props);
    }


    private taskBody() {
        return (<div><h2>The main task of this project is something we can call DEranking. </h2>

            <h3>Theoretical description:</h3>

            <p>Imagine that you have a database of text documents on a specific topic that are encyclopedia-like (i.e. descriptive) and you employ a BM25 ranking for retrieval.
            However, you want to steer users away from certain topics so you build a list of 'banned' keywords and essentially exclude all articles that contain any word from this list, in this way users will never see them.
            <br />This apprach has two big disadvantages:
            <ol>
                    <li> *it might be too much* You *significantly* reduce number of articles that the users can look through.
                    Also, you might discover that a lot of important articles dissapeared only because they had contained banned keyword,
            this happens because all documents are in one domain so they have a lot of overlap.</li>
                    <li>*it might be too little* Keyword based lists are very limited, they usually not take into account words that can be very easily associated with words you want to ban - synonyms, abbreviations or associations.</li>
                </ol>
            </p>
            <p>One of the approaches that solve both of those problems is to rank all the entries but the more keywords (and words related to them) a document has, the lower it's rank.
        Essentially, query would decide of a positive score, banned keywords would decide of a negative score. </p>

            <h3>Domain description</h3> <h4>(feel free to skip this part if you are not interested in Star Wars):</h4>
            <p>When Palpatine took over and dismantled the Galactic Republic, he effectively removed all information about Jedi order and related topic from all galactic databases.
            I was wondering how useful (and possible) such operation is, and in my opinion this was a bad strategy.
            With this move he had to not only remove all bad deeds done by the Jedi but also censor all "wins" of the sith that had anything to do with the order.
            I think propaganda would be better if instead of hiding the Jedi, he would just "downplay" their influcnce and "overplay" the importance of al other things.
            For example, if a user searches for 'order', they should see the 'Jedi order' but very very low in the results list instead, 'First order' should be pushed to the top.
        That kind of ordering will create an illusion of relevance when general populus searches for information. </p>


            <p>You can also think about it as a soft censorship.</p>

            <p>Note: since this approach is not removing articles from the list, it is still possible to find ones that have very high number of keywords you wanted to ban.
        This can be adressed by 'temperature' parameter (discussed in the implementation details).</p>
        </div>)

    }

    private solutionBody() {
        return <div>
            <p>
                We compute BM25 score for all indexed documents towards both query and banned keywords. Next we compute fasttext based cosine distance between the keywords and the documents.
                Lastly, we take top documents with score of query's BM25 minus keywords's BM25 multiplied by fasttext distance and temperature.
        </p>
            <p>
                Mathematical formulation: <br />
                Indexed documents <b>D</b>, <br />
                Query <b>Q</b>, <br />
                List of banned keywords <b>K</b>, <br />
                BM25 function <b>BM</b>, <br />
                temperature <b>T</b>, <br />
                Fasttext cosine distance <b>FT</b> <br />
                <b>R</b> - top <b>N</b> results.
        <br />
                <img src="https://latex.codecogs.com/png.latex?\bg_white&space;\fn_jvn&space;\large&space;D&space;=&space;[D_1,&space;D_2,&space;...,&space;D_p]&space;\\&space;S(D_n)&space;=&space;BM(D_n,&space;Q)&space;-&space;BM(D_n,&space;K)&space;\cdot&space;FT(D_n,&space;K)&space;\cdot&space;T&space;\\&space;R&space;=&space;argmax(S(D),N)" title="\large D = [D_1, D_2, ..., D_p] \\ S(D_n) = BM(D_n, Q) - BM(D_n, K) \cdot FT(D_n, K) \cdot T \\ R = argmax(S(D),N)" />
                <br />
By default the algorithm uses `T=2` but you can modify it by using a parameter, more on this in "how to navigate the page".
                {/* D = [D_1, D_2, ..., D_p]
\\
S(D_n) = BM(D_n, Q) - BM(D_n, K) \cdot FT(D_n, K) \cdot T
\\
R = argmax(S(D),N) */}
            </p>
        </div>
    }

    private howToNavigate() {
        return `how to fill in the fields, add parameters list (temperature, debug) note that more keywords => slower, this is because we did not precompute keyword vectors`
    }

    private techStackBody() {
        return `
        Typescript+bootstrap, python (flask + other libs), linux (azure hosted virtual machine), nginx,
        I'm using google domains for my malin.dev domain
        The code is  here: [github link]
        `
    }

    render() {
        return <div>

            <Accordion>
                {createCard("0", "How to navigate the page?", this.howToNavigate())}
                {createCard("1", "Task description", this.taskBody())}
                {createCard("2", "How it was solved?", this.solutionBody())}
                {createCard("3", "Implementation details (what model, how etc)", "body2")}
                {createCard("4", "Technological details (tech stack)", "body2")}
            </Accordion>
        </div>

    }
}