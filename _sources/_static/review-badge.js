/*
  NeurodeskEDU review badge

  How it works
  ────────────
  1. Every reviewed (or in-review) page embeds a <meta> tag:
       <meta name="nd-review-id" content="<uuid>">
     This is injected by a tiny Sphinx extension that reads the review_id
     from notebook metadata (.ipynb) or YAML front-matter (.md/.myst).

  2. This script fetches _static/reviews.json (generated at build time
     from the reviews repo issues) and looks up the review_id.

  3. A badge is injected near the top of the page showing review state,
     links to the review issue / DOI, and reviewer handles.
*/

(function () {
  "use strict";

  var REVIEWS_PATH = "_static/reviews.json";

  // -------------------------------------------------------------------
  // DOM helpers
  // -------------------------------------------------------------------

  function getContentRoot() {
    return (
      document.documentElement.getAttribute("data-content_root") ||
      document.documentElement.dataset.contentRoot ||
      ""
    );
  }

  function getReviewId() {
    var meta = document.querySelector('meta[name="nd-review-id"]');
    return meta ? (meta.getAttribute("content") || "").trim() : null;
  }

  function findInsertionTarget() {
    var sel = ["main", "article", ".bd-content", ".content"];
    for (var i = 0; i < sel.length; i++) {
      var el = document.querySelector(sel[i]);
      if (el) return el;
    }
    return document.body;
  }

  function findAuthorParagraph() {
    var paragraphs = document.querySelectorAll(
      "article.bd-article p, main p, article p"
    );
    for (var i = 0; i < paragraphs.length; i++) {
      var p = paragraphs[i];
      var label = p.querySelector("strong, b");
      if (label) {
        var t = (label.textContent || "").trim().toLowerCase();
        if (t === "author:" || t === "authors:") return p;
      }
      var pt = (p.textContent || "").trim().toLowerCase();
      if (pt.startsWith("author:") || pt.startsWith("authors:")) return p;
    }
    return null;
  }

  function insertAfter(node, ref) {
    var parent = ref && ref.parentNode;
    if (!parent) return false;
    parent.insertBefore(node, ref.nextSibling);
    return true;
  }

  // -------------------------------------------------------------------
  // Badge DOM
  // -------------------------------------------------------------------

  function createBadge(state, issueUrl, doiUrl, reviewers) {
    var badge = document.createElement("div");
    badge.className = "nd-review-badge nd-review-badge--" + state;

    var dot = document.createElement("span");
    dot.className = "nd-review-badge__dot";
    badge.appendChild(dot);

    var label = document.createElement("span");
    if (state === "reviewed") label.textContent = "Reviewed";
    else if (state === "in-progress") label.textContent = "Under review";
    else if (state === "stale") label.textContent = "Review out-of-date";
    else label.textContent = "Unreviewed";
    badge.appendChild(label);

    if (issueUrl) {
      badge.appendChild(document.createTextNode(" · "));
      var a = document.createElement("a");
      a.href = issueUrl;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = "review issue";
      badge.appendChild(a);
    }

    if (doiUrl) {
      badge.appendChild(document.createTextNode(" · "));
      var d = document.createElement("a");
      d.href = doiUrl;
      d.target = "_blank";
      d.rel = "noopener noreferrer";
      d.textContent = "DOI";
      badge.appendChild(d);
    }

    if (Array.isArray(reviewers) && reviewers.length) {
      var span = document.createElement("span");
      span.appendChild(
        document.createTextNode(
          " · reviewer" + (reviewers.length > 1 ? "s" : "") + ": "
        )
      );
      reviewers.forEach(function (login, idx) {
        var ra = document.createElement("a");
        ra.href = "https://github.com/" + encodeURIComponent(login);
        ra.target = "_blank";
        ra.rel = "noopener noreferrer";
        ra.textContent = "@" + login;
        span.appendChild(ra);
        if (idx < reviewers.length - 1)
          span.appendChild(document.createTextNode(", "));
      });
      badge.appendChild(span);
    }

    return badge;
  }

  // -------------------------------------------------------------------
  // Main
  // -------------------------------------------------------------------

  function main() {
    var reviewId = getReviewId();
    if (!reviewId) return; // page has no review_id — nothing to show

    var url = getContentRoot() + REVIEWS_PATH;

    fetch(url, { cache: "no-cache" })
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (registry) {
        if (!registry) return;

        var reviews = registry.reviews || {};
        var entry = reviews[reviewId] || null;
        var state = entry ? entry.state || "unreviewed" : "unreviewed";

        // Normalize: "queued" is displayed as "unreviewed" (grey badge)
        if (state === "queued") state = "unreviewed";

        // Only show reviewer names on the badge when fully reviewed
        var showReviewers =
          state === "reviewed" || state === "stale"
            ? entry && entry.reviewers
            : null;

        var badge = createBadge(
          state,
          entry && entry.review_issue_url,
          entry && entry.doi_url,
          showReviewers
        );

        var wrapper = document.createElement("div");
        wrapper.style.margin = "0 0 1rem 0";
        wrapper.appendChild(badge);

        var author = findAuthorParagraph();
        if (author && insertAfter(wrapper, author)) return;

        var target = findInsertionTarget();
        if (target.firstElementChild)
          target.insertBefore(wrapper, target.firstElementChild);
        else target.appendChild(wrapper);
      })
      .catch(function () {
        /* silently ignore network/parse errors */
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
