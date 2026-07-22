(function () {
  "use strict";

  var EXPECTED_SCHEMA_VERSION = 1;
  var ATHENS_TIME_ZONE = "Europe/Athens";
  var SEARCH_LIMIT = 8;
  var TRANSLATIONS = {
    el: {
      skipLink: "Μετάβαση στο εορτολόγιο",
      primaryNavigation: "Κύρια πλοήγηση",
      navCalendar: "Ημερολόγιο",
      navDate: "Ημερομηνία",
      navSearch: "Αναζήτηση",
      navSubscribe: "Εγγραφή",
      heroEyebrow: "Το ελληνικό εορτολόγιο",
      heroTitle: "Ποιος γιορτάζει σήμερα;",
      heroIntro: "Δείτε τις σημερινές ονομαστικές εορτές, εξερευνήστε κοντινές ημερομηνίες ή αναζητήστε ένα όνομα, ακόμη κι αν δεν είστε βέβαιοι για την ορθογραφία του.",
      todayHeading: "Γιορτάζουν σήμερα",
      loadingToday: "Φόρτωση σημερινών εορτών…",
      agendaEyebrow: "Προβολή 31 ημερών",
      agendaTitle: "Γύρω από τη σημερινή ημέρα",
      agendaLoading: "Δεκαπέντε ημέρες πριν και μετά από σήμερα.",
      returnToday: "Επιστροφή στο σήμερα",
      loadingCalendar: "Φόρτωση ημερολογίου…",
      calendarTools: "Εργαλεία ημερολογίου",
      dateEyebrow: "Εξερευνήστε το ημερολόγιο",
      dateTitle: "Επιλέξτε ημερομηνία",
      dateLabel: "Ημερομηνία",
      showDate: "Προβολή",
      searchEyebrow: "Ονόματα και εορτές",
      searchTitle: "Αναζήτηση στο έτος",
      searchLabel: "Όνομα ή εορτή",
      searchPlaceholder: "π.χ. Γιώργος ή Giorgos",
      searchGuidance: "Πληκτρολογήστε τουλάχιστον δύο χαρακτήρες, στα ελληνικά ή με λατινικούς χαρακτήρες.",
      subscriptionsEyebrow: "Πάντα ενημερωμένο",
      subscriptionsTitle: "Προσθέστε το εορτολόγιο στο ημερολόγιό σας",
      subscriptionsIntro: "Εγγραφείτε μία φορά. Η εφαρμογή ημερολογίου σας θα ανανεώνει το ίδιο αρχείο καθώς προστίθενται νέα έτη.",
      completeLabel: "Πλήρες εορτολόγιο",
      completeTitle: "Όλες οι ονομαστικές και εκκλησιαστικές εορτές",
      completeDescription: "Το πλήρες ελληνικό ορθόδοξο εορτολόγιο, με όλα τα διαθέσιμα ονόματα και τις εκκλησιαστικές εορτές.",
      essentialLabel: "Βασικό εορτολόγιο",
      essentialTitle: "100 δημοφιλέστερες ονομαστικές εορτές",
      essentialDescription: "Ένα πιο λιτό ημερολόγιο με τις δημοφιλέστερες ονομαστικές εορτές, χωρίς τίτλους εκκλησιαστικών εορτών.",
      subscribe: "Εγγραφή",
      download: "Λήψη .ics",
      subscriptionNote: "Η συχνότητα ανανέωσης εξαρτάται από την εφαρμογή ημερολογίου σας. Αν η εγγραφή δεν υποστηρίζεται, κατεβάστε και εισαγάγετε το αρχείο χειροκίνητα.",
      footerDescription: "Το ελληνικό εορτολόγιο, χωρίς παρακολούθηση ή διαφημίσεις.",
      repositoryPrefix: "Τα δεδομένα και τα ημερολόγια δημιουργούνται με το ανοικτού κώδικα",
      namedays: "Ονομαστικές εορτές",
      churchFeast: "Εκκλησιαστική εορτή",
      noCelebrationsToday: "Δεν υπάρχουν εορτές σήμερα.",
      noEvents: "Δεν υπάρχουν ονομαστικές ή εκκλησιαστικές εορτές.",
      noEventsOnDate: "Δεν υπάρχουν ονομαστικές ή εκκλησιαστικές εορτές αυτή την ημερομηνία.",
      today: "Σήμερα",
      noMatches: "Δεν βρέθηκαν κοντινά αποτελέσματα. Δοκιμάστε συντομότερη γραφή.",
      feast: "Εορτή",
      name: "Όνομα",
      calendarDates: "ημερολογιακές ημερομηνίες",
      primaryFeastDate: "Κύρια εορτή",
      additionalFeastDate: "Επιπλέον εορτή",
      notCelebratedThisYear: "Δεν εορτάζεται αυτό το έτος.",
      chooseDateFirst: "Επιλέξτε πρώτα μια ημερομηνία.",
      dateOutsideRange: "Η ημερομηνία βρίσκεται εκτός του διαθέσιμου εύρους.",
      fileServerError: "Ανοίξτε τον ιστότοπο μέσω τοπικού web server και όχι απευθείας ως αρχείο.",
      refreshError: "Ανανεώστε τη σελίδα και δοκιμάστε ξανά.",
      loadError: "Δεν ήταν δυνατή η φόρτωση των δεδομένων του ημερολογίου. ",
    },
    en: {
      skipLink: "Skip to calendar",
      primaryNavigation: "Primary navigation",
      navCalendar: "Calendar",
      navDate: "Date",
      navSearch: "Search",
      navSubscribe: "Subscribe",
      heroEyebrow: "The Greek nameday calendar",
      heroTitle: "Who is celebrating today?",
      heroIntro: "See today’s namedays, explore nearby dates, or find a name even when you are unsure of its spelling.",
      todayHeading: "Celebrated today",
      loadingToday: "Loading today’s calendar…",
      agendaEyebrow: "Thirty-one day view",
      agendaTitle: "Around today",
      agendaLoading: "Fifteen days before and after today.",
      returnToday: "Return to today",
      loadingCalendar: "Loading calendar…",
      calendarTools: "Calendar tools",
      dateEyebrow: "Explore the calendar",
      dateTitle: "Choose a date",
      dateLabel: "Calendar date",
      showDate: "Show date",
      searchEyebrow: "Names and feasts",
      searchTitle: "Search the year",
      searchLabel: "Name or feast",
      searchPlaceholder: "Try Γιώργος or Giorgos",
      searchGuidance: "Type at least two characters using Greek or Latin letters.",
      subscriptionsEyebrow: "Always up to date",
      subscriptionsTitle: "Add the nameday calendar to your calendar",
      subscriptionsIntro: "Subscribe once. Your calendar app can refresh the same feed as new years are added.",
      completeLabel: "Complete calendar",
      completeTitle: "Every nameday and church feast",
      completeDescription: "The full Greek Orthodox calendar, including all bundled names and church observances.",
      essentialLabel: "Essential calendar",
      essentialTitle: "Top 100 namedays",
      essentialDescription: "A lighter feed containing the most popular nameday identity groups, without church feast titles.",
      subscribe: "Subscribe",
      download: "Download .ics",
      subscriptionNote: "Subscription refresh timing is controlled by your calendar app. On unsupported browsers, download and import the file manually.",
      footerDescription: "Greek namedays and feasts, without tracking or advertising.",
      repositoryPrefix: "Data and calendars are generated with the open-source",
      namedays: "Namedays",
      churchFeast: "Church feast",
      noCelebrationsToday: "No celebrations today.",
      noEvents: "No namedays or feasts.",
      noEventsOnDate: "No namedays or feasts on this date.",
      today: "Today",
      noMatches: "No close matches found. Try a shorter spelling.",
      feast: "Feast",
      name: "Name",
      calendarDates: "calendar dates",
      primaryFeastDate: "Primary feast",
      additionalFeastDate: "Additional feast",
      notCelebratedThisYear: "Not celebrated this year.",
      chooseDateFirst: "Choose a date first.",
      dateOutsideRange: "That date is outside the available calendar range.",
      fileServerError: "Open the site through a local web server instead of as a file.",
      refreshError: "Please refresh the page and try again.",
      loadError: "Calendar data could not be loaded. ",
    },
  };

  var state = {
    branding: null,
    config: null,
    today: null,
    days: new Map(),
    searchEntries: [],
    language: "el",
    selectedDate: null,
  };

  var elements = {
    metaDescription: document.getElementById("meta-description"),
    languageButtons: document.querySelectorAll("[data-language]"),
    todayWeekday: document.getElementById("today-weekday"),
    todayNumber: document.getElementById("today-number"),
    todayMonth: document.getElementById("today-month"),
    todayEvents: document.getElementById("today-events"),
    agendaRange: document.getElementById("agenda-range"),
    agendaList: document.getElementById("agenda-list"),
    returnToday: document.getElementById("return-today"),
    dateForm: document.getElementById("date-form"),
    dateInput: document.getElementById("date-input"),
    dateRangeCopy: document.getElementById("date-range-copy"),
    dateResult: document.getElementById("date-result"),
    searchInput: document.getElementById("search-input"),
    searchYearCopy: document.getElementById("search-year-copy"),
    searchResults: document.getElementById("search-results"),
    completeSubscribe: document.getElementById("complete-subscribe"),
    popularSubscribe: document.getElementById("popular-subscribe"),
    completeRange: document.getElementById("complete-range"),
    popularRange: document.getElementById("popular-range"),
    dataUpdated: document.getElementById("data-updated"),
  };

  var fullDateFormatter;
  var shortDateFormatter;
  var weekdayFormatter;
  var monthFormatter;

  function t(key) {
    return TRANSLATIONS[state.language][key];
  }

  function locale() {
    return state.language === "el" ? "el-GR" : "en-GB";
  }

  function configureFormatters() {
    var currentLocale = locale();
    fullDateFormatter = new Intl.DateTimeFormat(currentLocale, {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    });
    shortDateFormatter = new Intl.DateTimeFormat(currentLocale, {
      day: "numeric",
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    });
    weekdayFormatter = new Intl.DateTimeFormat(currentLocale, {
      weekday: "short",
      timeZone: "UTC",
    });
    monthFormatter = new Intl.DateTimeFormat(currentLocale, {
      month: "short",
      timeZone: "UTC",
    });
  }

  function storedLanguage() {
    var fallback = state.branding.default_language;
    try {
      var value = window.localStorage.getItem(state.branding.language_storage_key);
      return TRANSLATIONS[value] && state.branding.locales[value] ? value : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function rememberLanguage(language) {
    try {
      window.localStorage.setItem(state.branding.language_storage_key, language);
    } catch (error) {
      return;
    }
  }

  function applyStaticTranslations() {
    var localizedBranding = state.branding.locales[state.language];
    document.documentElement.lang = state.language;
    document.title = localizedBranding.title;
    elements.metaDescription.content = localizedBranding.description;
    document.querySelectorAll("[data-i18n]").forEach(function (node) {
      node.textContent = t(node.dataset.i18n);
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach(function (node) {
      node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel));
    });
    document.querySelectorAll("[data-brand-home]").forEach(function (node) {
      node.setAttribute("aria-label", localizedBranding.home_label);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (node) {
      node.placeholder = t(node.dataset.i18nPlaceholder);
    });
    elements.languageButtons.forEach(function (button) {
      button.setAttribute("aria-pressed", String(button.dataset.language === state.language));
    });
  }

  function loadJson(path) {
    return fetch(path, { cache: "no-store" }).then(function (response) {
      if (!response.ok) {
        throw new Error("Could not load " + path + " (HTTP " + response.status + ")");
      }
      return response.json();
    });
  }

  function assertSchema(payload, label) {
    if (!payload || payload.schema_version !== EXPECTED_SCHEMA_VERSION) {
      throw new Error(label + " uses an unsupported data format.");
    }
  }

  function parseIsoDate(value) {
    var parts = value.split("-");
    return new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
  }

  function toIsoDate(value) {
    return [
      value.getUTCFullYear(),
      String(value.getUTCMonth() + 1).padStart(2, "0"),
      String(value.getUTCDate()).padStart(2, "0"),
    ].join("-");
  }

  function addDays(isoDate, amount) {
    var value = parseIsoDate(isoDate);
    value.setUTCDate(value.getUTCDate() + amount);
    return toIsoDate(value);
  }

  function dateIsWithin(value, minimum, maximum) {
    return value >= minimum && value <= maximum;
  }

  function currentDateInAthens(fallback) {
    try {
      var formatter = new Intl.DateTimeFormat("en-GB", {
        timeZone: ATHENS_TIME_ZONE,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
      var parts = formatter.formatToParts(new Date());
      var values = {};
      parts.forEach(function (part) {
        if (part.type !== "literal") {
          values[part.type] = part.value;
        }
      });
      return values.year + "-" + values.month + "-" + values.day;
    } catch (error) {
      return fallback;
    }
  }

  function element(tagName, className, text) {
    var node = document.createElement(tagName);
    if (className) {
      node.className = className;
    }
    if (typeof text === "string") {
      node.textContent = text;
    }
    return node;
  }

  function emptyDay() {
    return { namedays: [], primary_namedays: [], observances: [], commemorations: [] };
  }

  function dayData(isoDate) {
    return state.days.get(isoDate) || emptyDay();
  }

  function appendEventGroup(container, label, values, type, primaryValues) {
    if (!values.length) {
      return;
    }
    var group = element("div", "event-group is-" + type);
    group.appendChild(element("span", "event-label", label));
    var eventText = element("p", "event-text");
    if (type === "nameday") {
      var primaryNames = new Set(primaryValues || []);
      values.forEach(function (value, index) {
        if (index > 0) {
          eventText.appendChild(document.createTextNode(", "));
        }
        var isPrimary = primaryNames.has(value);
        var feastLabel = isPrimary ? t("primaryFeastDate") : t("additionalFeastDate");
        var name = element(
          "span",
          "event-name" + (isPrimary ? " is-primary" : " is-secondary"),
          value
        );
        name.title = feastLabel;
        name.appendChild(element("span", "visually-hidden", " (" + feastLabel + ")"));
        eventText.appendChild(name);
      });
    } else {
      eventText.textContent = values.join(", ");
    }
    group.appendChild(eventText);
    container.appendChild(group);
  }

  function appendEvents(container, data, emptyMessage, includeCommemorations) {
    var feastValues = data.observances.slice();
    if (includeCommemorations) {
      (data.commemorations || []).forEach(function (title) {
        if (feastValues.indexOf(title) === -1) {
          feastValues.push(title);
        }
      });
    }
    if (!data.namedays.length && !feastValues.length) {
      container.appendChild(element("p", "empty-copy", emptyMessage));
      return;
    }
    var groups = element("div", "event-groups");
    appendEventGroup(
      groups,
      t("namedays"),
      data.namedays,
      "nameday",
      data.primary_namedays
    );
    appendEventGroup(groups, t("churchFeast"), feastValues, "feast", []);
    container.appendChild(groups);
  }

  function renderToday() {
    var parsed = parseIsoDate(state.today);
    elements.todayWeekday.textContent = new Intl.DateTimeFormat(locale(), {
      weekday: "long",
      timeZone: "UTC",
    }).format(parsed);
    elements.todayNumber.textContent = String(parsed.getUTCDate());
    elements.todayMonth.textContent = new Intl.DateTimeFormat(locale(), {
      month: "long",
      timeZone: "UTC",
    }).format(parsed);
    elements.todayEvents.replaceChildren();
    appendEvents(elements.todayEvents, dayData(state.today), t("noCelebrationsToday"));
  }

  function buildAgendaDay(isoDate) {
    var parsed = parseIsoDate(isoDate);
    var article = element("article", "agenda-day");
    article.id = "day-" + isoDate;
    if (isoDate === state.today) {
      article.classList.add("is-today");
      article.setAttribute("aria-current", "date");
    }

    article.appendChild(element("h3", "visually-hidden", fullDateFormatter.format(parsed)));
    var dateBlock = element("time", "agenda-date");
    dateBlock.dateTime = isoDate;
    dateBlock.appendChild(element("span", "agenda-weekday", weekdayFormatter.format(parsed)));
    dateBlock.appendChild(element("span", "agenda-number", String(parsed.getUTCDate())));
    dateBlock.appendChild(element("span", "agenda-month", monthFormatter.format(parsed)));
    article.appendChild(dateBlock);

    var events = element("div", "agenda-events");
    if (isoDate === state.today) {
      events.appendChild(element("span", "today-badge", t("today")));
    }
    appendEvents(events, dayData(isoDate), t("noEvents"), true);
    article.appendChild(events);
    return article;
  }

  function showTodayAtTop(behavior) {
    var today = document.getElementById("day-" + state.today);
    if (!today) {
      return;
    }
    elements.agendaList.scrollTo({ top: today.offsetTop, behavior: behavior });
  }

  function renderAgenda() {
    var first = addDays(state.today, -15);
    var last = addDays(state.today, 15);
    elements.agendaRange.textContent = shortDateFormatter.format(parseIsoDate(first)) +
      " — " + shortDateFormatter.format(parseIsoDate(last));

    var fragment = document.createDocumentFragment();
    for (var offset = -15; offset <= 15; offset += 1) {
      fragment.appendChild(buildAgendaDay(addDays(state.today, offset)));
    }
    elements.agendaList.replaceChildren(fragment);
    window.requestAnimationFrame(function () {
      showTodayAtTop("auto");
    });
  }

  function renderDateResult(isoDate) {
    state.selectedDate = isoDate;
    var container = element("section", "result-panel");
    container.appendChild(element("h3", null, fullDateFormatter.format(parseIsoDate(isoDate))));
    appendEvents(container, dayData(isoDate), t("noEventsOnDate"), true);
    elements.dateResult.replaceChildren(container);
  }

  function renderDateError(message) {
    state.selectedDate = null;
    elements.dateResult.replaceChildren(element("p", "error-copy", message));
  }

  function normalizeSearchText(value) {
    return value
      .trim()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase("el-GR")
      .replace(/ς/g, "σ");
  }

  var GREEK_LATIN_LETTERS = {
    α: "a", β: "v", γ: "g", δ: "d", ε: "e", ζ: "z", η: "i",
    θ: "th", ι: "i", κ: "k", λ: "l", μ: "m", ν: "n", ξ: "x",
    ο: "o", π: "p", ρ: "r", σ: "s", τ: "t", υ: "y", φ: "f",
    χ: "x", ψ: "ps", ω: "o",
  };
  var GREEK_LATIN_DIGRAPHS = {
    αι: "ai", αυ: "av", ει: "ei", ευ: "ev", οι: "oi", ου: "ou",
    υι: "yi", γγ: "gg", γκ: "gk", μπ: "mp", ντ: "nt", τσ: "ts",
    τζ: "tz",
  };
  var GREEK_PHONETIC_DIGRAPHS = {
    αι: "e", αυ: "av", ει: "i", ευ: "ev", οι: "i", ου: "ou",
    υι: "i", γγ: "gg", γκ: "g", μπ: "b", ντ: "d", τσ: "ts",
    τζ: "tz",
  };

  function normalizeLatinSearchText(value) {
    return value
      .toLocaleLowerCase("en-US")
      .replace(/ch/g, "x")
      .replace(/ph/g, "f")
      .replace(/ks/g, "x")
      .replace(/qu/g, "k")
      .replace(/c/g, "k")
      .replace(/w/g, "o")
      .replace(/y/g, "i");
  }

  function transliterateGreek(value, phonetic) {
    var normalized = normalizeSearchText(value);
    var digraphs = phonetic ? GREEK_PHONETIC_DIGRAPHS : GREEK_LATIN_DIGRAPHS;
    var output = "";
    var index = 0;
    while (index < normalized.length) {
      var pair = normalized.slice(index, index + 2);
      if (digraphs[pair]) {
        output += digraphs[pair];
        index += 2;
      } else {
        var letter = normalized.charAt(index);
        output += GREEK_LATIN_LETTERS[letter] || letter;
        index += 1;
      }
    }
    return normalizeLatinSearchText(output);
  }

  function searchFormsForEntry(entry) {
    var forms = [entry.normalized];
    var orthographic = transliterateGreek(entry.label, false);
    var phonetic = transliterateGreek(entry.label, true);
    [orthographic, phonetic].forEach(function (form) {
      if (form && forms.indexOf(form) === -1) {
        forms.push(form);
      }
    });
    return forms;
  }

  function searchFormsForQuery(query) {
    var normalized = normalizeSearchText(query);
    var forms = [normalized];
    if (/[a-z]/i.test(normalized)) {
      var latin = normalizeLatinSearchText(normalized);
      if (forms.indexOf(latin) === -1) {
        forms.push(latin);
      }
    }
    return forms;
  }

  function damerauLevenshtein(left, right) {
    var rows = left.length + 1;
    var columns = right.length + 1;
    var matrix = new Array(rows);
    var row;
    var column;

    for (row = 0; row < rows; row += 1) {
      matrix[row] = new Array(columns);
      matrix[row][0] = row;
    }
    for (column = 0; column < columns; column += 1) {
      matrix[0][column] = column;
    }

    for (row = 1; row < rows; row += 1) {
      for (column = 1; column < columns; column += 1) {
        var substitutionCost = left.charAt(row - 1) === right.charAt(column - 1) ? 0 : 1;
        matrix[row][column] = Math.min(
          matrix[row - 1][column] + 1,
          matrix[row][column - 1] + 1,
          matrix[row - 1][column - 1] + substitutionCost
        );
        if (
          row > 1 &&
          column > 1 &&
          left.charAt(row - 1) === right.charAt(column - 2) &&
          left.charAt(row - 2) === right.charAt(column - 1)
        ) {
          matrix[row][column] = Math.min(
            matrix[row][column],
            matrix[row - 2][column - 2] + substitutionCost
          );
        }
      }
    }
    return matrix[rows - 1][columns - 1];
  }

  function fuzzyRank(query, candidate) {
    if (candidate === query) {
      return { category: 4, score: 1 };
    }
    if (candidate.indexOf(query) === 0) {
      return { category: 3, score: 0.88 + (query.length / candidate.length) * 0.1 };
    }
    if (candidate.indexOf(query) !== -1) {
      return { category: 2, score: 0.72 + (query.length / candidate.length) * 0.12 };
    }

    var distance = damerauLevenshtein(query, candidate);
    var score = 1 - (distance / Math.max(query.length, candidate.length));
    var threshold = query.length <= 3 ? 0.64 : query.length <= 5 ? 0.52 : 0.42;
    if (score < threshold) {
      return null;
    }
    return { category: 1, score: score };
  }

  function betterRank(left, right) {
    return !right || left.category > right.category ||
      (left.category === right.category && left.score > right.score);
  }

  function bestFuzzyRank(queryForms, candidateForms) {
    var best = null;
    queryForms.forEach(function (query) {
      candidateForms.forEach(function (candidate) {
        var rank = fuzzyRank(query, candidate);
        if (rank && betterRank(rank, best)) {
          best = rank;
        }
      });
    });
    return best;
  }

  function search(query) {
    var queryForms = searchFormsForQuery(query);
    if (queryForms[0].length < 2) {
      return [];
    }
    return state.searchEntries
      .map(function (entry) {
        var rank = bestFuzzyRank(queryForms, entry.searchForms);
        return rank ? { entry: entry, rank: rank } : null;
      })
      .filter(function (value) { return value !== null; })
      .sort(function (left, right) {
        if (left.rank.category !== right.rank.category) {
          return right.rank.category - left.rank.category;
        }
        if (left.rank.score !== right.rank.score) {
          return right.rank.score - left.rank.score;
        }
        var leftPopularity = left.entry.popularity === null ? -1 : left.entry.popularity;
        var rightPopularity = right.entry.popularity === null ? -1 : right.entry.popularity;
        if (leftPopularity !== rightPopularity) {
          return rightPopularity - leftPopularity;
        }
        return left.entry.label.localeCompare(right.entry.label, "el");
      })
      .slice(0, SEARCH_LIMIT);
  }

  function showSearchResultDate(value) {
    elements.dateInput.value = value;
    renderDateResult(value);
    document.getElementById("date-lookup").scrollIntoView({ behavior: "smooth" });
  }

  function resultDateButton(value, isPrimary) {
    var parsed = parseIsoDate(value);
    var label = isPrimary ? t("primaryFeastDate") : t("additionalFeastDate");
    var button = element(
      "button",
      "search-result-date" + (isPrimary ? " is-primary" : ""),
      shortDateFormatter.format(parsed)
    );
    button.type = "button";
    button.title = label;
    button.setAttribute("aria-label", label + ": " + fullDateFormatter.format(parsed));
    button.addEventListener("click", function () {
      showSearchResultDate(value);
    });
    return button;
  }

  function renderSearchResults(query) {
    var normalized = normalizeSearchText(query);
    elements.searchResults.replaceChildren();
    if (normalized.length < 2) {
      return;
    }

    var matches = search(query);
    if (!matches.length) {
      elements.searchResults.appendChild(element("p", "empty-copy", t("noMatches")));
      return;
    }

    var list = element("ul", "search-result-list");
    matches.forEach(function (match) {
      var item = element("li");
      var card = element("div", "search-result-card");
      var heading = element("div", "search-result-heading");
      heading.appendChild(element("span", "search-result-name", match.entry.label));
      heading.appendChild(element(
        "span",
        "result-kind" + (match.entry.kind === "feast" ? " is-feast" : ""),
        match.entry.kind === "feast" ? t("feast") : t("name")
      ));
      card.appendChild(heading);

      var dates = element("div", "search-result-dates");
      dates.setAttribute("role", "group");
      dates.setAttribute("aria-label", t("calendarDates"));
      match.entry.dates.forEach(function (value, index) {
        dates.appendChild(resultDateButton(value, index === 0));
      });
      if (!match.entry.dates.length) {
        dates.appendChild(element(
          "span",
          "search-result-no-date",
          t("notCelebratedThisYear")
        ));
      }
      card.appendChild(dates);
      item.appendChild(card);
      list.appendChild(item);
    });
    elements.searchResults.appendChild(list);
  }

  function subscriptionHref(path) {
    try {
      var target = new URL(path, window.location.href);
      if (target.protocol === "http:" || target.protocol === "https:") {
        target.protocol = "webcal:";
      }
      return target.href;
    } catch (error) {
      return path;
    }
  }

  function setSubscriptionDetails(key, link, range) {
    var details = state.config.subscriptions[key];
    link.href = subscriptionHref(details.path);
    range.textContent = details.from_year + "–" + details.to_year + " · " +
      details.event_count.toLocaleString(locale()) + " " + t("calendarDates");
  }

  function formatGeneratedAt(value) {
    var parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }
    return new Intl.DateTimeFormat(locale(), {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: ATHENS_TIME_ZONE,
    }).format(parsed);
  }

  function configureInterface() {
    var minimum = state.config.lookup.min_date;
    var maximum = state.config.lookup.max_date;
    elements.dateInput.min = minimum;
    elements.dateInput.max = maximum;
    if (!elements.dateInput.value || !dateIsWithin(elements.dateInput.value, minimum, maximum)) {
      elements.dateInput.value = dateIsWithin(state.today, minimum, maximum) ? state.today : minimum;
    }
    if (state.language === "el") {
      elements.dateRangeCopy.textContent = "Επιλέξτε ημερομηνία από " +
        shortDateFormatter.format(parseIsoDate(minimum)) + " έως " +
        shortDateFormatter.format(parseIsoDate(maximum)) + ".";
      elements.searchYearCopy.textContent = "Αναζητήστε ονόματα και εορτές για το " +
        state.config.search_year + ". Μπορείτε να γράψετε με ελληνικούς ή λατινικούς χαρακτήρες· οι τόνοι και τα μικρά ορθογραφικά λάθη δεν αποτελούν πρόβλημα.";
      elements.dataUpdated.textContent = "Το ημερολόγιο δημιουργήθηκε στις " +
        formatGeneratedAt(state.config.generated_at) + ".";
    } else {
      elements.dateRangeCopy.textContent = "Choose a date from " +
        shortDateFormatter.format(parseIsoDate(minimum)) + " through " +
        shortDateFormatter.format(parseIsoDate(maximum)) + ".";
      elements.searchYearCopy.textContent = "Search names and feasts in " +
        state.config.search_year + ". Greek and Latin letters are supported, and small spelling mistakes are welcome.";
      elements.dataUpdated.textContent = "Calendar bundle generated " +
        formatGeneratedAt(state.config.generated_at) + ".";
    }
    setSubscriptionDetails("complete", elements.completeSubscribe, elements.completeRange);
    setSubscriptionDetails("top_100", elements.popularSubscribe, elements.popularRange);
  }

  function setLanguage(language, persist) {
    state.language = TRANSLATIONS[language] && state.branding.locales[language] ?
      language : state.branding.default_language;
    if (persist) {
      rememberLanguage(state.language);
    }
    configureFormatters();
    applyStaticTranslations();
    if (!state.config) {
      return;
    }
    configureInterface();
    renderToday();
    renderAgenda();
    if (state.selectedDate) {
      renderDateResult(state.selectedDate);
    }
    renderSearchResults(elements.searchInput.value);
  }

  function registerInteractions() {
    elements.languageButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        if (button.dataset.language !== state.language) {
          setLanguage(button.dataset.language, true);
        }
      });
    });
    elements.returnToday.addEventListener("click", function () {
      showTodayAtTop("smooth");
    });
    elements.dateForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var selected = elements.dateInput.value;
      if (!selected) {
        renderDateError(t("chooseDateFirst"));
        return;
      }
      if (!dateIsWithin(selected, state.config.lookup.min_date, state.config.lookup.max_date)) {
        renderDateError(t("dateOutsideRange"));
        return;
      }
      renderDateResult(selected);
    });

    var searchTimer;
    elements.searchInput.addEventListener("input", function () {
      window.clearTimeout(searchTimer);
      var query = elements.searchInput.value;
      searchTimer = window.setTimeout(function () {
        renderSearchResults(query);
      }, 120);
    });
  }

  function renderFatalError(error) {
    var message = t("loadError") + (window.location.protocol === "file:" ?
      t("fileServerError") : t("refreshError"));
    elements.todayEvents.replaceChildren(element("p", "error-copy", message));
    elements.agendaList.replaceChildren(element("p", "status-card", message));
    console.error(error);
  }

  function initialize() {
    return loadJson("branding.json")
      .then(function (branding) {
        assertSchema(branding, "Website branding");
        state.branding = branding;
        setLanguage(storedLanguage(), false);
        registerInteractions();
        return loadJson("data/config.json");
      })
      .then(function (config) {
        assertSchema(config, "Website configuration");
        state.config = config;
        var liveToday = currentDateInAthens(config.today);
        var availableMinimum = config.calendar_years[0] + "-01-01";
        var availableMaximum = config.calendar_years[config.calendar_years.length - 1] + "-12-31";
        state.today = dateIsWithin(liveToday, availableMinimum, availableMaximum) ? liveToday : config.today;
        var calendarRequests = config.calendar_years.map(function (year) {
          return loadJson("data/calendar-" + year + ".json");
        });
        var searchRequest = loadJson("data/search-" + config.search_year + ".json");
        return Promise.all([Promise.all(calendarRequests), searchRequest]);
      })
      .then(function (payloads) {
        payloads[0].forEach(function (calendar) {
          assertSchema(calendar, "Calendar " + calendar.year);
          calendar.days.forEach(function (day) {
            state.days.set(day.date, day);
          });
        });
        assertSchema(payloads[1], "Search index");
        state.searchEntries = payloads[1].entries.map(function (entry) {
          entry.searchForms = searchFormsForEntry(entry);
          return entry;
        });
        configureInterface();
        renderToday();
        renderAgenda();
      })
      .catch(renderFatalError);
  }

  initialize();
}());
