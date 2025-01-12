using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentimentAnalysis.Sentiment_Analysis.Model
{
    public class SentenceModel
    {
        string sentence { get; set; }
        List<string> sentenceTokens { get; set; }
        int positiveFrequency {  get; set; }
        int negativeFrequency { get; set; }
        List<string> negativeWords { get; set;}
        List<string> positiveWords { get; set;}
    }
}
