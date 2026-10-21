# Module 2 Checkpoint 1 — AI Content Studio Design

## 1. Business facts

| Key | Value |
|---|---|
| name | Sweet Crumbs |
| type | Bakery |
| city | Lahore |
| hours | 9 am to 10 pm |
| delivery_fee | 200 PKR |
| free_delivery_minimum | 3,000 PKR |
| customers | Families and university students |
| prices | Chocolate Cake: 1,500 PKR; Cupcake: 250 PKR; Brownie: 300 PKR; Mango Tart: 0 PKR (coming soon) |

## 2. Social media tones

| Tone | Description sent to the AI |
|---|---|
| fun | Playful and full of energy, with short sentences |
| premium | Elegant and calm, focused on quality |
| urgent | Exciting and time-sensitive, without inventing deadlines |

## 3. Model selection

| Job | Model and temperature | Why |
|---|---|---|
| Customer chat and facts | Ollama llama3.2, 0.2 | More consistent, factual answers |
| Menu descriptions | Ollama llama3.2, 0.8 | More creative marketing language |
| Social media posts | Ollama llama3.2, 0.8 | More varied tone and style |
| Price lookup | Python dictionary; no AI | Exact prices and no token cost |

## 4. Feature test results

| You type | Expected | Pass? |
|---|---|---|
| `/menu` | Numbered menu; Mango Tart skipped | Pending |
| `/post fun` | Streaming fun post | Pending |
| `/post premium` | Streaming premium post | Pending |
| `/post urgent` | Streaming urgent post | Pending |
| `/post pirate` | Defaults to fun tone | Pending |
| `/price CUPCAKE` | Cupcake costs 250 PKR | Pending |
| `/price mango tart` | Coming soon | Pending |
| `/price pizza` | Not on our menu | Pending |
| `My name is Ali`, then `What is my name?` | Remembers name | Pending |
| `/reset`, then `What is my name?` | Does not know name | Pending |
| Press Enter without text | Asks again | Pending |
| `BYE` | Goodbye and session report | Pending |

Replace Pending with Pass or Fail only after testing.

## 5. Session report checks

- Chat answers are counted.
- Menu descriptions are counted.
- Posts are counted.
- Price commands are counted.
- Total AI tokens and elapsed AI time are printed.
- Dictionary price lookups and skipped products do not call the AI.
