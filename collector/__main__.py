#################################################
# The Event Registry API classes
# Retrieves articles, events and other
# news data from the Event Registry service.
#
# Contains additional classes used for retrieving
# and processing

import argparse

import eventregistry as ER
import json
import sys
import os
# TODO add tqdm for progress


#######################################
# Helper Functions
#######################################

def create_folder_directory(path):
    """Creates the folder structure associated with the `path`
    Args:
        path (str): The path to the given file.
    """

    # get the folder structure path
    normpath = os.path.normpath(path)
    split_path = normpath.split(os.sep)
    del split_path[-1]
    # reconstruct the folder structure and create
    # the directories if they do not exist yet
    directory = os.sep.join(split_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_as_array(file, articles):
    """Save the articles as an array of objects

    Args:
        file (obj): The file object to which we wish to write.
        articles (iter): The iterator with all of the acquired
            articles.
    """

    json.dump([a for a in articles], file)


def save_as_separate_line(file, articles):
    """Saves the article objects in separate lines

    Args:
        file (obj): The file object to which we wish to write.
        articles (iter): The iterator with all of the acquired
            articles.
    """

    for article in articles:
        try:
            # write the article json to the file
            json.dump(article, file)
            file.write("\n")
        except:
            continue


def save_result_in_file(articles, file_path, save_format=None):
    """Saves the articles into the provided file in the given format.

    Args:
        articles (list(obj)): The list of objects containing
            the article information.
        file_path (str): The path to the file the objects will be stored.
        save_format (str): The format in which we wish to store the
            articles (Default: None). Options:
                'array' - The articles are wrapped into an array. Should not
                    be used when storing query results into the same file.
                None - The articles are stored line-by-line in the file.

    """

    # create the folder directory
    create_folder_directory(file_path)
    # store the events
    with open(file_path, 'a') as f:
        # save the
        if save_format == 'array':
            save_as_array(f, articles)
        else:
            save_as_separate_line(f, articles)


#######################################
# Main Classes
#######################################

class URI:

    def __init__(self, keyword, uri):
        """ Initializes the keyword concept pair
            used then in the event registry collector class

        Args:
            keyword (str): The source keyword for concept
            concept (str): the wikipedia concept associated
                with the source keyword

        """
        self.__keyword = keyword
        self.__uri = uri


    def get_keyword(self):
        """Gets the keyword value

        Returns:
            str: the source keyword

        """
        return self.__keyword


    def get_uri(self):
        """Gets the wikipedia concept

        Returns:
            str: the wikipedia concept

        """
        return self.__uri


    def __eq__(self, other):
        """Compares if the instances are the same"""
        return self.__uri == other


    def __ne__(self, other):
        """Compares if the instances are not the same"""
        return not self == other



class EventRegistryCollector:

    def __init__(self, api_key, max_repeat_request=-1):
        """Initializes the event registry collector

        Args:
            api_key (str): The api key generated by the event
                registry service for the user

            max_repeat_request (int): The number of maximum
                requests that can be repeated if something
                goes wrong. If -1, repeat indefinately
                (Default: -1)

        """

        # initialize the event registry instance
        self._er = ER.EventRegistry(
            apiKey = api_key,
            repeatFailedRequestCount = max_repeat_request
        )


    def get_concepts(self, concepts):
        """Get the list of event registry concepts

        Args:
            concepts (list(str)): The list of concepts for
                retrieving the concept URIs.

        Returns:
            list(URI): A list of URI objects with the given
                concept URIs.

        """
        return [URI(k, self._er.getConceptUri(k)) for k in concepts]


    def get_categories(self, categories):
        """Get the list of event registry concepts

        Args:
            categories (list(str)): The list of categories for
                retrieving the categories URIs.

        Returns:
            list(URI): A list of URI objects with the given
                categories URIs.

        """
        return [URI(k, self._er.getCategoryUri(k)) for k in categories]


    def get_sources(self, sources):
        """Get the list of source uris

        Args:
            sources (list(str)): The list of sources for
                retrieving the source URIs.

        Returns:
            list(URI): A list of URI objects with the given
                source URIs.

        """
        return [URI(k, self._er.getSourceUri(k)) for k in sources]


    def get_articles(self, keywords=None, concepts=None, categories=None, sources=None,
         languages=None, date_start=None, date_end=None, sort_by='date', sort_by_asc=False,
         max_items=-1, save_to_file=None, save_format=None):
        """Get the event registry articles

        Args:
            keywords (list(str)): The list of keywords the articles
                should contain (Default: None).
            concepts (list(str)): The list of concepts the articles
                should contain (Default: None).
            categories (list(str)): The list of categories the articles
                should be in (Default: None).
            sources (list(str)): The list of sources from which to
                retrieve the articles (Default: None).
            language (list(str)): The list of languages the articles
                should be written in (Default: None).
            date_start (date): The start date from which the articles
                should be acquired.If None, it starts from the first
                date supported by Event Registry (Default: None).
            date_end (date): The end date until which the articles
                should be acquired. If None, it ends at the day of
                collecting (Default: None).
            sort_by (str): The sorting attribute, see https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-articles
                (Default: 'date').
            sort_by_asc (bool): If the documents should be sorted in
                ascending (True) or descending order (False) (Default: False).
            max_items (int): The maximum number of articles to retrieve,
                where -1 means return all matching articles (Default: -1).
            save_to_file (str): The path to which we wish to store the articles.
                If None, the articles are not stored. In addition, if the same
                file is used for multiple queries, the new articles will be
                appended to the existing ones (Default: None).
            save_format (str): The format in which the articles are stored. (Default: None)
                Options:
                    'array' - The articles are wrapped into an array. Should not
                        be used when storing query results into the same file.
                    None - The articles are stored line-by-line in the file.

        Returns:
            Iterator: The iterator which goes through all retrieved articles.

        """

        # setup the event registry parameters
        er_keywords = ER.QueryItems.AND(keywords) if keywords else None
        er_concepts = ER.QueryItems.AND([c.get_uri() for c in self.get_concepts(concepts)]) if concepts else None
        er_categories = ER.QueryItems.AND([c.get_uri() for c in self.get_categories(categories)]) if categories else None
        er_sources = ER.QueryItems.OR([c.get_uri() for c in self.get_sources(sources)]) if sources else None
        er_lang = ER.QueryItems.OR(languages) if languages else None

        # when saving to file check the last date and use it as start date
        if save_to_file and os.path.isfile(save_to_file):
            with open(save_to_file) as in_file:
                # get all lines
                lines = in_file.readlines()
                if len(lines) > 0:
                    last_article = json.loads(lines[-1])
                    # check if last event in right location
                    date_start = last_article['date']

        # creates the query articles object
        q = ER.QueryArticlesIter(
            keywords = er_keywords,
            conceptUri = er_concepts,
            categoryUri = er_categories,
            sourceUri = er_sources,
            dateStart = date_start,
            dateEnd = date_end,
            lang = er_lang
        )

        # execute the query and return the iterator
        articles = q.execQuery(self._er, sortBy=sort_by, sortByAsc=sort_by_asc, maxItems=max_items)

        if save_to_file:
            save_result_in_file(articles, save_to_file, save_format)

        # return the articles for other use
        return articles


    def get_events(self, keywords=None, concepts=None, categories=None, sources=None,
         languages=None, date_start=None, date_end=None, sort_by='date', sort_by_asc=False,
         max_items=-1, save_to_file=None, save_format=None):
        """Get the event registry events

        Args:
            keywords (list(str)): The list of keywords the articles
                should contain (Default: None).
            concepts (list(str)): The list of concepts the articles
                should contain (Default: None).
            categories (list(str)): The list of categories the articles
                should be in (Default: None).
            sources (list(str)): The list of sources from which to
                retrieve the articles (Default: None).
            language (list(str)): The list of languages the articles
                should be written in (Default: None).
            date_start (date): The start date from which the articles
                should be acquired.If None, it starts from the first
                date supported by Event Registry (Default: None).
            date_end (date): The end date until which the articles
                should be acquired. If None, it ends at the day of
                collecting (Default: None).
            sort_by (str): The sorting attribute, see https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-articles
                (Default: 'date').
            sort_by_asc (bool): If the documents should be sorted in
                ascending (True) or descending order (False) (Default: False).
            max_items (int): The maximum number of articles to retrieve,
                where -1 means return all matching articles (Default: -1).
            save_to_file (str): The path to which we wish to store the articles.
                If None, the articles are not stored. In addition, if the same
                file is used for multiple queries, the new articles will be
                appended to the existing ones (Default: None).
            save_format (str): The format in which the articles are stored. (Default: None)
                Options:
                    'array' - The articles are wrapped into an array. Should not
                        be used when storing query results into the same file.
                    None - The articles are stored line-by-line in the file.

        Returns:
            Iterator: The iterator which goes through all retrieved articles.

        """

        # setup the event registry parameters
        er_keywords = ER.QueryItems.AND(keywords) if keywords else None
        er_concepts = ER.QueryItems.AND([c.get_uri() for c in self.get_concepts(concepts)]) if concepts else None
        er_categories = ER.QueryItems.AND([c.get_uri() for c in self.get_categories(categories)]) if categories else None
        er_sources = ER.QueryItems.OR([c.get_uri() for c in self.get_sources(sources)]) if sources else None
        er_lang = ER.QueryItems.OR(languages) if languages else None

        # when saving to file check the last date and use it as start date
        if save_to_file and os.path.isfile(save_to_file):
            with open(save_to_file) as in_file:
                # get all lines
                lines = in_file.readlines()
                if len(lines) > 0:
                    last_article = json.loads(lines[-1])
                    # check if last event in right location
                    date_start = last_article['eventDate']

        # creates the query articles object
        q = ER.QueryEventsIter(
            keywords = er_keywords,
            conceptUri = er_concepts,
            categoryUri = er_categories,
            sourceUri = er_sources,
            dateStart = date_start,
            dateEnd = date_end,
            lang = er_lang
        )

        # execute the query and return the iterator
        events = q.execQuery(self._er, sortBy=sort_by, sortByAsc=sort_by_asc, maxItems=max_items)

        if save_to_file:
            # saves the events into
            save_result_in_file(events, save_to_file, save_format)

        # return the events for other use
        return events


    def get_event_articles(self, event_id, keywords=None, concepts=None, categories=None,
        sources=None, languages=None, date_start=None, date_end=None, sort_by='date',
        sort_by_asc=False, max_items=-1, save_to_file=None, save_format=None):
        """Get the articles of a certain event

        Args:
            event_id (str): The event id from which we get the
                news articles within the event.
            keywords (list(str)): The list of keywords the articles
                should contain (Default: None).
            concepts (list(str)): The list of concepts the articles
                should contain (Default: None).
            categories (list(str)): The list of categories the articles
                should be in (Default: None).
            sources (list(str)): The list of sources from which to
                retrieve the articles (Default: None).
            language (list(str)): The list of languages the articles
                should be written in (Default: None).
            date_start (date): The start date from which the articles
                should be acquired.If None, it starts from the first
                date supported by Event Registry (Default: None).
            date_end (date): The end date until which the articles
                should be acquired. If None, it ends at the day of
                collecting (Default: None).
            sort_by (str): The sorting attribute, see https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-articles
                (Default: 'date').
            sort_by_asc (bool): If the documents should be sorted in
                ascending (True) or descending order (False) (Default: False).
            max_items (int): The maximum number of articles to retrieve,
                where -1 means return all matching articles (Default: -1).
            save_to_file (str): The path to which we wish to store the articles.
                If None, the articles are not stored. In addition, if the same
                file is used for multiple queries, the new articles will be
                appended to the existing ones (Default: None).
            save_format (str): The format in which the articles are stored. (Default: None)
                Options:
                    'array' - The articles are wrapped into an array. Should not
                        be used when storing query results into the same file.
                    None - The articles are stored line-by-line in the file.

        Returns:
            Iterator: The iterator which goes through all retrieved articles.

        """

        # setup the event registry parameters
        er_keywords = ER.QueryItems.AND(keywords) if keywords else None
        er_concepts = ER.QueryItems.AND([c.get_uri() for c in self.get_concepts(concepts)]) if concepts else None
        er_categories = ER.QueryItems.AND([c.get_uri() for c in self.get_categories(categories)]) if categories else None
        er_sources = ER.QueryItems.OR([c.get_uri() for c in self.get_sources(sources)]) if sources else None
        er_lang = ER.QueryItems.OR(languages) if languages else None

        # creates the query event articles object
        q = ER.QueryEventArticlesIter(
            event_id,
            keywords = er_keywords,
            conceptUri = er_concepts,
            categoryUri = er_categories,
            sourceUri = er_sources,
            dateStart = date_start,
            dateEnd = date_end,
            lang = er_lang
        )

        # execute the query and return the iterator
        articles = q.execQuery(self._er, sortBy=sort_by, sortByAsc=sort_by_asc, maxItems=max_items)

        if save_to_file:
            # saves the articles into
            save_result_in_file(articles, save_to_file, save_format)

        # return the articles for other use
        return articles


    def get_event_articles_from_file(self, event_ids_file, event_file_type='events',
        keywords=None, concepts=None, categories=None, sources=None, languages=None,
        date_start=None, date_end=None, sort_by='date', sort_by_asc=False, max_items=-1,
        save_to_folder=None, save_format=None):
        """Gets the event articles from a list of event ids stored in a
            separate file and store them in their own event json file.

        Args:
            event_ids_file (str): The event ids file path containing
                the event ids.
            event_file_type (str): The event file type (Default: 'events'). Options:
                - 'plain', where each line of the file contains a single event id
                - 'events', where each line of the file contains an event registry event object
                    with the 'url' attribute (used as the event id)
            keywords (list(str)): The list of keywords the articles
                should contain (Default: None).
            concepts (list(str)): The list of concepts the articles
                should contain (Default: None).
            categories (list(str)): The list of categories the articles
                should be in (Default: None).
            sources (list(str)): The list of sources from which to
                retrieve the articles (Default: None).
            language (list(str)): The list of languages the articles
                should be written in (Default: None).
            date_start (date): The start date from which the articles
                should be acquired.If None, it starts from the first
                date supported by Event Registry (Default: None).
            date_end (date): The end date until which the articles
                should be acquired. If None, it ends at the day of
                collecting (Default: None).
            sort_by (str): The sorting attribute, see https://github.com/EventRegistry/event-registry-python/wiki/Searching-for-articles
                (Default: 'date').
            sort_by_asc (bool): If the documents should be sorted in
                ascending (True) or descending order (False) (Default: False).
            max_items (int): The maximum number of articles to retrieve,
                where -1 means return all matching articles (Default: -1).
            save_to_folder (str): The folder in which we wish to store the event articles.
                If None, the articles are not stored (Default: None).
            save_format (str): The format in which the articles are stored. (Default: None)
                Options:
                    'array' - The articles are wrapped into an array.
                    None - The articles are stored line-by-line in the file.

        """

        # check if the event ids file exists
        if not(event_ids_file and os.path.isfile(event_ids_file)):
            raise Exception('get_event_articles_list: event_ids_file doesn\'t exist')

        # open the file with the given event ids
        event_ids = []
        with open(event_ids_file, 'r') as f:
            lines = f.readlines()

            if len(lines) == 0:
                raise Exception('get_event_articles_list: event_ids_file is empty')

            if event_file_type == 'events':
                # the file contains whole event objects, extract only the ids
                for line in lines:
                    line = json.loads(line)
                    event_ids.append(line['uri'].strip())
            else:
                # each line of the file is a separate event id
                for line in lines:
                    event_ids.append(line.strip())

        event_articles = []

        for event_id in event_ids:
            # setup the event path
            event_path = "{}/{}.json".format(save_to_folder, event_id) if save_to_folder else None

            # get the event articles
            articles = self.get_event_articles(event_id, keywords, concepts,
                categories, sources, languages, date_start, date_end, sort_by,
                sort_by_asc, max_items, event_path, save_format)

            # store the articles and the event id
            event_articles.append({
                "event_id": event_id,
                "articles": articles
            })

        # return the list of event articles
        return event_articles



if __name__=='__main__':
    # parse command line arguments
    argparser = argparse.ArgumentParser(description="Service for retrieving event registry articles")

    argparser.add_argument('--api_key',            type=str, default=None, help="Event Registry API key")
    argparser.add_argument('--max_repeat_request', type=int, default=-1,   help="The maximum number of repeated requests")

    subparsers = argparser.add_subparsers(help='command')

    ###################################
    # Articles Query
    ###################################

    argparser_articles = subparsers.add_parser('articles', help="Collects the articles based on some parameters")
    argparser_articles.set_defaults(action='articles')
    # query related attributes
    argparser_articles.add_argument('--keywords',     type=str,  default=None,   help="The comma separated keywords the articles should contain")
    argparser_articles.add_argument('--concepts',     type=str,  default=None,   help="The comma separated concepts the articles should be associated with")
    argparser_articles.add_argument('--categories',   type=str,  default=None,   help="The comma separated categories of the collected articles")
    argparser_articles.add_argument('--sources',      type=str,  default=None,   help="The comma separated media sources that published the articles")
    argparser_articles.add_argument('--languages',    type=str,  default=None,   help="The comma separated languages of the articles")
    argparser_articles.add_argument('--date_start',   type=str,  default=None,   help="The start date of the articles")
    argparser_articles.add_argument('--date_end',     type=str,  default=None,   help="The end date of the articles")
    # data retrieving attributes
    argparser_articles.add_argument('--sort_by',      type=str,  default='date', help="The sort order of articles")
    argparser_articles.add_argument('--sort_by_asc',  type=bool, default=True,   help="The direction of the sort")
    argparser_articles.add_argument('--max_items',    type=int,  default=-1,     help="The number of articles to collect")
    # data storing values
    argparser_articles.add_argument('--save_to_file', type=str,  default=None,   help="The path to the file to store the articles")
    argparser_articles.add_argument('--save_format',  type=str,  default=None,   help="The format in which to store the articles")

    ###################################
    # Events Query
    ###################################

    argparser_events = subparsers.add_parser('events', help="Collects the events based on some parameters")
    argparser_events.set_defaults(action='events')
    # query related attributes
    argparser_events.add_argument('--keywords',     type=str,  default=None,   help="The comma separated keywords the events should contain")
    argparser_events.add_argument('--concepts',     type=str,  default=None,   help="The comma separated concepts the events should be associated with")
    argparser_events.add_argument('--categories',   type=str,  default=None,   help="The comma separated categories of the collected events")
    argparser_events.add_argument('--sources',      type=str,  default=None,   help="The comma separated media sources that published the events")
    argparser_events.add_argument('--languages',    type=str,  default=None,   help="The comma separated languages of the events")
    argparser_events.add_argument('--date_start',   type=str,  default=None,   help="The start date of the events")
    argparser_events.add_argument('--date_end',     type=str,  default=None,   help="The end date of the events")
    # data retrieving attributes
    argparser_events.add_argument('--sort_by',      type=str,  default='date', help="The sort order of events")
    argparser_events.add_argument('--sort_by_asc',  type=bool, default=True,   help="The direction of the sort")
    argparser_events.add_argument('--max_items',    type=int,  default=-1,     help="The number of events to collect")
    # data storing values
    argparser_events.add_argument('--save_to_file', type=str,  default=None,   help="The path to the file to store the events")
    argparser_events.add_argument('--save_format',  type=str,  default=None,   help="The format in which to store the events")

    ###################################
    # Event Articles Query
    ###################################

    argparser_events = subparsers.add_parser('event_articles', help="Collects the event articles based on some parameters")
    argparser_events.set_defaults(action='event_articles')
    # query related attributes
    argparser_events.add_argument('--event_id',     type=str,  default=None,   help="The event id of the event for which we wish the articles")
    argparser_events.add_argument('--keywords',     type=str,  default=None,   help="The comma separated keywords the event articles should contain")
    argparser_events.add_argument('--concepts',     type=str,  default=None,   help="The comma separated concepts the event articles should be associated with")
    argparser_events.add_argument('--categories',   type=str,  default=None,   help="The comma separated categories of the collected event articles")
    argparser_events.add_argument('--sources',      type=str,  default=None,   help="The comma separated media sources that published the event articles")
    argparser_events.add_argument('--languages',    type=str,  default=None,   help="The comma separated languages of the event articles")
    argparser_events.add_argument('--date_start',   type=str,  default=None,   help="The start date of the event articles")
    argparser_events.add_argument('--date_end',     type=str,  default=None,   help="The end date of the event articles")
    # data retrieving attributes
    argparser_events.add_argument('--sort_by',      type=str,  default='rel', help="The sort order of event articles")
    argparser_events.add_argument('--sort_by_asc',  type=bool, default=True,   help="The direction of the sort")
    argparser_events.add_argument('--max_items',    type=int,  default=-1,     help="The number of event articles to collect")
    # data storing values
    argparser_events.add_argument('--save_to_file', type=str,  default=None,   help="The path to the file to store the event articles")
    argparser_events.add_argument('--save_format',  type=str,  default=None,   help="The format in which to store the event articles")

    ###################################
    # Event Articles List Query
    ###################################

    argparser_events = subparsers.add_parser('event_articles_from_file', help="Collects the event articles from a file and based on some parameters")
    argparser_events.set_defaults(action='event_articles_from_file')
    # query related attributes
    argparser_events.add_argument('--event_ids_file',  type=str,  default=None,     help="The file which contains the event ids")
    argparser_events.add_argument('--event_file_type', type=str,  default='events', help="The type of the event file type. Options: 'events', 'plain'")
    argparser_events.add_argument('--keywords',        type=str,  default=None,     help="The comma separated keywords the event articles should contain")
    argparser_events.add_argument('--concepts',        type=str,  default=None,     help="The comma separated concepts the event articles should be associated with")
    argparser_events.add_argument('--categories',      type=str,  default=None,     help="The comma separated categories of the collected event articles")
    argparser_events.add_argument('--sources',         type=str,  default=None,     help="The comma separated media sources that published the event articles")
    argparser_events.add_argument('--languages',       type=str,  default=None,     help="The comma separated languages of the event articles")
    argparser_events.add_argument('--date_start',      type=str,  default=None,     help="The start date of the event articles")
    argparser_events.add_argument('--date_end',        type=str,  default=None,     help="The end date of the event articles")
    # data retrieving attributes
    argparser_events.add_argument('--sort_by',         type=str,  default='rel',   help="The sort order of event articles")
    argparser_events.add_argument('--sort_by_asc',     type=bool, default=True,     help="The direction of the sort")
    argparser_events.add_argument('--max_items',       type=int,  default=-1,       help="The number of event articles to collect")
    # data storing values
    argparser_events.add_argument('--save_to_file',    type=str,  default=None,     help="The path to the folder to store the event articles files")
    argparser_events.add_argument('--save_format',     type=str,  default=None,     help="The format in which to store the event articles")

    try:
        # parse the arguments and call whatever function was selected
        args = argparser.parse_args()

        # event registry API values
        api_key = args.api_key

        if not api_key:
            raise Exception('Attribute api_key must be specified')

        max_repeat_request = args.max_repeat_request

        # query related attributes
        keywords   = [k.strip() for k in args.keywords.split(',')]   if args.keywords else None
        concepts   = [c.strip() for c in args.concepts.split(',')]   if args.concepts else None
        categories = [c.strip() for c in args.categories.split(',')] if args.categories else None
        sources    = [s.strip() for s in args.sources.split(',')]    if args.sources else None
        languages  = [l.strip() for l in args.languages.split(',')]  if args.languages else None
        date_start = args.date_start if args.date_start else None
        date_end   = args.date_end   if args.date_end   else None
        # data retrieving attributes
        sort_by     = args.sort_by
        sort_by_asc = args.sort_by_asc in [True, 'True', 'true', '1', 't', 'y']
        max_items   = args.max_items
        # data storing values
        save_to_file = args.save_to_file if args.save_to_file else None
        save_format  = args.save_format  if args.save_format  else None

        # initialize and execute query
        er = EventRegistryCollector(api_key=api_key, max_repeat_request=max_repeat_request)

        if args.action == 'articles':
            # execute the articles query
            er.get_articles(keywords=keywords, concepts=concepts, categories=categories,
                sources=sources, languages=languages, date_start=date_start, date_end=date_end,
                sort_by=sort_by, sort_by_asc=sort_by_asc, max_items=max_items,
                save_to_file=save_to_file, save_format=save_format)

        elif args.action == 'events':
            # execute the events query
            er.get_events(keywords=keywords, concepts=concepts, categories=categories,
                sources=sources, languages=languages, date_start=date_start, date_end=date_end,
                sort_by=sort_by, sort_by_asc=sort_by_asc, max_items=max_items,
                save_to_file=save_to_file, save_format=save_format)

        elif args.action == 'event_articles':
            # get query specific information
            event_id = args.event_id if args.event_id else None
            # execute the events query
            er.get_event_articles(event_id, keywords=keywords, concepts=concepts, categories=categories,
                sources=sources, languages=languages, date_start=date_start, date_end=date_end,
                sort_by=sort_by, sort_by_asc=sort_by_asc, max_items=max_items,
                save_to_file=save_to_file, save_format=save_format)

        elif args.action == 'event_articles_from_file':
            # get query specific information
            event_ids_file  = args.event_ids_file  if args.event_ids_file  else None
            event_file_type = args.event_file_type if args.event_file_type else None

            # execute the events query
            er.get_event_articles_from_file(event_ids_file, event_file_type=event_file_type, keywords=keywords,
                concepts=concepts, categories=categories, sources=sources, languages=languages,
                date_start=date_start, date_end=date_end, sort_by=sort_by, sort_by_asc=sort_by_asc,
                max_items=max_items, save_to_folder=save_to_file, save_format=save_format)

        else:
            raise Exception('Argument command is unknown: {}'.format(args.command))
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
