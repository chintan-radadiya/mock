const fs = require('node:fs');
const CAT = require('../app/core');
const mcq = (id, prompt, options, answer, topic, explanation) => ({ id, type: 'MCQ', prompt, options: options.map((text, i) => ({ id: String.fromCharCode(65 + i), text })), answer, topic, explanation });
const tita = (id, prompt, answer, topic, explanation) => ({ id, type: 'TITA', prompt, answer: [answer], topic, explanation });
const demo = {
  schemaVersion: 1, testType: 'full', id: 'cat-studio-demo', revision: 1, title: 'Explore the exam experience', demo: true,
  description: 'A short, original sample across all three sections. Try the tools before a real attempt.',
  sections: [
    { code: 'VARC', groups: [
      { id: 'demo-rc', title: 'RC · Learning through retrieval', stimulus: 'Students often judge learning by how familiar a page feels on a second reading. Yet familiarity can conceal gaps in recall. A learner who closes the book and tries to explain an idea may feel less fluent, but the effort reveals what remains uncertain.\n\nThis does not make rereading useless. A return to the text after an attempted explanation can target specific gaps. The distinction is between rereading to avoid effort and rereading to answer a question that effort has exposed.', questions: [
        mcq('demo-v1', 'Which statement best captures the central argument?', ['Rereading always harms recall.', 'Fluency is a reliable measure of understanding.', 'Attempting recall can reveal gaps that targeted rereading then addresses.', 'Books should be closed permanently after one reading.'], 'C', 'Reading comprehension', 'The author combines effortful recall with targeted rereading rather than rejecting rereading.'),
        mcq('demo-v2', 'The author would most likely recommend:', ['Explaining an idea without the text, then checking uncertain points.', 'Reading a page until every word feels familiar.', 'Avoiding difficult explanations.', 'Measuring learning only by reading speed.'], 'A', 'Reading comprehension', 'This sequence follows the method described in the second paragraph.')
      ] },
      { id: 'demo-va', title: 'Verbal ability', questions: [tita('demo-v3', 'Arrange the sentences into a coherent paragraph. Enter the sequence.\n\n1. This stored water supports the seedlings during dry weeks.\n2. Farmers first collect rainwater in small tanks.\n3. They then channel the stored water towards newly planted beds.', '231', 'Para jumble', 'Collection comes first, channeling follows, and the final sentence explains the benefit.')] }
    ] },
    { code: 'DILR', groups: [{ id: 'demo-di', title: 'DI · Bookshop sales', stimulus: 'A bookshop sold the following numbers of books.\n\n             Monday   Tuesday\nFiction        30        45\nScience        20        25\nHistory        10        20\n\nAll figures are numbers of books, not sales revenue.', questions: [
      tita('demo-d1', 'How many books were sold on Tuesday?', '90', 'Tables', '45 + 25 + 20 = 90.'),
      mcq('demo-d2', 'Which category had the largest percentage increase from Monday to Tuesday?', ['Fiction', 'Science', 'History', 'All three were equal'], 'C', 'Tables', 'History doubled from 10 to 20, an increase of 100%.'),
      tita('demo-d3', 'What percentage of Monday sales consisted of fiction books?', '50', 'Tables', '30 out of 60 books is 50%.')
    ] }] },
    { code: 'QA', groups: [
      { id: 'demo-qa1', title: 'Arithmetic', questions: [mcq('demo-q1', 'A price rises by 20% and then falls by 20%. What is the net change?', ['No change', '4% decrease', '4% increase', '2% decrease'], 'B', 'Percentages', '100 × 1.2 × 0.8 = 96, a decrease of 4%.')] },
      { id: 'demo-qa2', title: 'Algebra', questions: [tita('demo-q2', 'If 3x + 7 = 34, find x.', '9', 'Linear equations', 'Subtract 7 and divide by 3: x = 27 / 3 = 9.')] },
      { id: 'demo-qa3', title: 'Arithmetic', questions: [mcq('demo-q3', 'A train covers 180 km in 3 hours. What is its average speed?', ['45 km/h', '50 km/h', '60 km/h', '90 km/h'], 'C', 'Speed and distance', 'Speed = distance / time = 180 / 3 = 60 km/h.')] }
    ] }
  ]
};
const real = ['varc-section-6','dilr-section-1','simcat-2'].map(name => CAT.validate(JSON.parse(fs.readFileSync('samples/'+name+'.json','utf8'))));
CAT.validate(demo);
fs.writeFileSync('samples/sample-full-mock.json', JSON.stringify(demo, null, 2));
fs.writeFileSync('app/data.js', 'window.DEMO_TEST = ' + JSON.stringify(demo) + ';\nwindow.BUNDLED_TESTS = ' + JSON.stringify([...real,demo]) + ';\n');
console.log('Bundled three imported tests and original three-section demo.');
