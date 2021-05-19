import React, { Component } from "react";
import { Accordion, Card } from "react-bootstrap";
import "../styles/about.css";
import basics from "../imgs/basic.png";
import basics_debug from "../imgs/basic_debug.png";
import results_with_score from "../imgs/results_with_score.png";
import results_debug_full from "../imgs/results_debug_full.png";
import results_debug_temp from "../imgs/results_debug_temp.png";
import results from "../imgs/results.png";

const createCard: any = (key: string, title: string, body: any) => (
  <Card>
    <Accordion.Toggle as={Card.Header} eventKey={key}>
      {title}
    </Accordion.Toggle>
    <Accordion.Collapse eventKey={key}>
      <Card.Body>{body}</Card.Body>
    </Accordion.Collapse>
  </Card>
);
export default class AboutPage extends Component<{}> {
  private taskBody() {
    return (
      <div>
        <h2>
          The main task of this project is something we can call DEranking.{" "}
        </h2>
        <h3>Theoretical description:</h3>
        <p>
          Imagine that you have a database of text documents on a specific topic
          that are encyclopedia-like (i.e. descriptive) and you employ a BM25
          ranking for retrieval. However, you want to steer users away from
          certain topics so you build a list of 'banned' keywords and
          essentially exclude all articles that contain any word from this list,
          in this way users will never see them.
          <br />
          This apprach has two big disadvantages:
          <ol>
            <li>
              {" "}
              *it might be too much* You *significantly* reduce number of
              articles that the users can look through. Also, you might discover
              that a lot of important articles dissapeared only because they had
              contained banned keyword, this happens because all documents are
              in one domain so they have a lot of overlap.
            </li>
            <li>
              *it might be too little* Keyword based lists are very limited,
              they usually not take into account words that can be very easily
              associated with words you want to ban - synonyms, abbreviations or
              associations.
            </li>
          </ol>
        </p>
        <p>
          One of the approaches that solve both of those problems is to rank all
          the entries but the more keywords (and words related to them) a
          document has, the lower it's rank. Essentially, query would decide of
          a positive score, banned keywords would decide of a negative score.{" "}
        </p>
        <h3>Domain description</h3>{" "}
        <h4>
          (feel free to skip this part if you are not interested in Star Wars):
        </h4>
        <p>
          When Palpatine took over and dismantled the Galactic Republic, he
          effectively removed all information about Jedi order and related topic
          from all galactic databases. I was wondering how useful (and possible)
          such operation is, and in my opinion this was a bad strategy. With
          this move he had to not only remove all bad deeds done by the Jedi but
          also censor all "wins" of the sith that had anything to do with the
          order. I think propaganda would be better if instead of hiding the
          Jedi, he would just "downplay" their influcnce and "overplay" the
          importance of al other things. For example, if a user searches for
          'order', they should see the 'Jedi order' but very very low in the
          results list instead, 'First order' should be pushed to the top. That
          kind of ordering will create an illusion of relevance when general
          populus searches for information.{" "}
        </p>
        <p>You can also think about it as a soft censorship.</p>
        <p>
          Note: since this approach is not removing articles from the list, it
          is still possible to find ones that have very high number of keywords
          you wanted to ban. This can be adressed by 'temperature' parameter (as
          shown in the "How it was solved?" card).
        </p>
      </div>
    );
  }

  private solutionBody() {
    return (
      <div>
        <p>
          We compute BM25 score for all indexed documents towards both query and
          banned keywords. Next we compute fasttext based cosine distance
          between the keywords and the documents. Lastly, we take top documents
          with score of query's BM25 minus keywords's BM25 multiplied by
          fasttext distance and temperature.
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
          <img
            alt=""
            src="https://latex.codecogs.com/png.latex?\bg_white&space;\fn_jvn&space;\large&space;D&space;=&space;[D_1,&space;D_2,&space;...,&space;D_p]&space;\\&space;S(D_n)&space;=&space;BM(D_n,&space;Q)&space;-&space;BM(D_n,&space;K)&space;\cdot&space;FT(D_n,&space;K)&space;\cdot&space;T&space;\\&space;R&space;=&space;argmax(S(D),N)"
            title="\large D = [D_1, D_2, ..., D_p] \\ S(D_n) = BM(D_n, Q) - BM(D_n, K) \cdot FT(D_n, K) \cdot T \\ R = argmax(S(D),N)"
          />
          <br />
          By default the algorithm uses `T=2` but you can modify it by using a
          parameter, more on this in "how to navigate the page".
          {/* D = [D_1, D_2, ..., D_p]
\\
S(D_n) = BM(D_n, Q) - BM(D_n, K) \cdot FT(D_n, K) \cdot T
\\
R = argmax(S(D),N) */}
          <br />
          <br />
          Temperature can be used in three ways:
          <ul>
            <li>
              T &gt; 0 indicates that keywords should be considered as
              "negative" and the models should try to derank them.
            </li>
            <li>T = 0 indicates no change to the original BM model.</li>
            <li>
              T &lt; 0 indicates that keywords should be considered as
              "positive" and the models should try to rank them higher.
            </li>
          </ul>
        </p>
      </div>
    );
  }

  private howToNavigate() {
    return (
      <div>
        <h1>Basic search</h1>
        <p>
          To start searching navigate to "Search" tab or click{" "}
          <a href="https://www.malin.dev/search">here</a>. The main page should
          look like below:
          <br />
          <img src={basics} alt="basic" />
          <br />
        </p>
        <p>
          To search please fill in "Phrase" field, you should also fill in
          "keywords" field to provide keywords for deranking, they should be
          written in form of a comma separated list like shown below.
          <br />
          Now, press the green "search" button. <br />
          After some time, you will see two columns: "Original results" and
          "Modified results". <br />
          <img src={results} alt="results" />
          <br />
        </p>
        <p>
          First column represents results sorted by BM25L model, second column
          corresponds to results ordered by modified value (according to the
          formula explained in "How was it solved?").
          <br />
          Note: the results are clickable so you can actually visit the
          wookiepedia page that a given result links to. <br />
          You can also notice a checkbox "scores", after searching and selecting
          it, you should be able to see the scores computed for each record.
          <br />
          <img src={results_with_score} alt="results_with_score" />
          <br />
        </p>

        <h1>Advanced options</h1>
        <p>
          In order to modify the temperature parameter and see more details you
          will have to navigate to search page with debug parameter{" "}
          <a href="https://www.malin.dev/search?debug=true">
            https://www.malin.dev/search?debug=true
          </a>
          .<br />
          After entering you will see two more options appeared, temp and debug
          checkbox. <br />
          <img src={basics_debug} alt="results_with_score" />
          <br />
        </p>
        <p>
          First one allows you to play with temperature parameter, you can
          change it to a selected value and press the green "Search" button
          again.
          <br />
          <img src={results_debug_temp} alt="results_debug_temp" />
          <br />{" "}
        </p>
        <p>
          The "debug" checkbox allows you to learn more about the scores
          returned by the model.
          <br />
          <img src={results_debug_full} alt="results_debug_full" />
          <br />{" "}
        </p>
      </div>
    );
  }

  private techStackBody() {
    return (
      <p>
        <ul>
          <li>MongoDb with python driver </li>
          <li>TypeScript + bootstrap </li>
          <li>
            Python with libs: flask + FastText + rank_bm25 and others, please
            see requirements.txt in git repo
          </li>
          <li>
            Page is hosted on azure VM Standard E2as_v4 with Ubuntu, I am using
            nginx to host both React and Flask apps.{" "}
          </li>
          <li>
            To register the domain (malin.dev), I am using google domains.
          </li>
          <li>Link to github will be provided soon.</li>
        </ul>
      </p>
    );
  }

  private implementationDetailsBody() {
    return (
      <p>
        All data was collected from{" "}
        <a href="https://starwars.fandom.com/wiki/Main_Page">Wookiepedia</a> -
        fan made wiki for star wars. I have collected almost all articles as of
        May 10th. You might find that some information might be incomplete or
        missing, this is because I have had some troubles parsing certain
        websites due to non-english characters. For each page I have extracted
        the "content" (i.e. text without banners) and removed all references. It
        was then piped through preprocessing pipeline (see
        src\index\preprocessing_pipeline.py file for details) - it tokenized
        whole article, cleaned some words and stemmed them. Whatever was left
        was used to build BM and fasttext models.
        <br />
        <p>
          There are a few important libraries used in this project: <br />
          <a href="https://github.com/dorianbrown/rank_bm25">rank_bm25</a> which
          helped me to compute BM25L model that I've used for the retrieval
          part.
          <br />
          <a href="https://github.com/facebookresearch/fastText">
            fastText
          </a>{" "}
          that I have used for training the fastText model.
          <br />
        </p>
      </p>
    );
  }

  render() {
    return (
      <div>
        Please take a look at "How to navigate the page?" if you encounter any
        issues, it lists some tips to see more scores. Otherwise, just contact
        me.
        <Accordion>
          {createCard("0", "How to navigate the page?", this.howToNavigate())}
          {createCard("1", "Task description", this.taskBody())}
          {createCard("2", "How was it solved?", this.solutionBody())}
          {createCard(
            "3",
            "Implementation details (what model, how etc)",
            this.implementationDetailsBody()
          )}
          {createCard(
            "4",
            "Technological details (tech stack)",
            this.techStackBody()
          )}
        </Accordion>
      </div>
    );
  }
}
