let
    fxGithubCsv = (FileName as text) as table =>
        let
            Source = Csv.Document(
                Web.Contents(GitHubRawBaseUrl & FileName),
                [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
            ),
            PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
        in
            PromotedHeaders
in
    fxGithubCsv
