i want to change ui of this website without breaking the logic 
1. i want to make it modern and classic ( similar to claude website but with more and different colors ).
2. use that classic fonts from that claude website.
3. also do some glass and at some places star types moving animations as well.
4. suggest some changes that can make our design much better ( in implementation plan ).
5. do light and dark mode ( and i like space dark with some star background with glass effect, ) and light theme with that that classy claude colors but add some moree to it as well.
6. give me some surprice ( not bugs though ).

now build complete implementation plan

# LearnWise — Premium UI Redesign

A complete, zero-logic-breaking visual overhaul of LearnWise to achieve a **modern-classic aesthetic** inspired by Claude's warmth + a space-dark sci-fi palette — with glass effects, animated star fields, serif/editorial typography, light/dark themes, and hand-crafted micro-animations throughout.

---

## Design Vision

| Dimension | Dark Mode (Space) | Light Mode (Classy) |
|---|---|---|
| **Background** | Deep-space `#070B14` + animated parallax stars (3 layers, CSS-only) | Warm cream `#FAF8F5` with subtle paper grain |
| **Cards/Glass** | Frosted deep-navy with `backdrop-filter: blur(24px)` | White glass with warm amber tint, soft shadows |
| **Primary accent** | Electric indigo `#7C6EFA` + cyan `#00D4FF` aurora | Warm terracotta `#CC785C` + golden `#E8A87C` |
| **Secondary accent** | Emerald `#00E5B0` for XP | Forest `#2D6A4F` for XP |
| **Font — Display** | **Playfair Display** (classical, editorial — Claude's font) | Same, with slightly heavier weight |
| **Font — Body** | **Inter** (current, keep) | **Inter** |
| **Font — Mono** | **JetBrains Mono** (for code/labels) | Same |
| **Animations** | Star field parallax, aurora glow, floating orbs | Gentle dust-mote float, warm pulse |

### Claude-inspired touches
- Rounded serif display headings (Playfair Display)
- Warm, human color palette with natural depth
- Generous whitespace, understated borders
- Micro-copy that breathes (letter-spacing on labels)

### Surprise 🎁
- **Constellation cursor trail** — tiny star dots follow the mouse in dark mode (CSS/JS, no performance impact)
- **XP celebration burst** — when XP is earned, a confetti-star burst animates from the XP badge
- **Aurora top-bar** — a slowly-shifting rainbow gradient on the sidebar header (subtle, elegant)
- **Typing cursor** on the login headline (blinks like a terminal)
- **"Skill tree" visual** on Dashboard — activity nodes connected by glowing lines instead of a plain grid

---

## New Files

| File | Purpose |
|---|---|
| `src/theme.css` | All CSS custom properties for dark + light themes, star/aurora keyframes |
| `src/components/StarField.jsx` | Animated parallax star background component (CSS-only stars, no canvas) |
| `src/components/ThemeToggle.jsx` | Sun/moon toggle button, persists to `localStorage` |
| `src/components/AuroraBar.jsx` | Colour-shifting gradient bar for sidebar header |
| `src/components/XPBurst.jsx` | Confetti-star celebration burst triggered on XP earn |
| `src/hooks/useTheme.js` | Theme state hook with localStorage persistence |

---

## Proposed Changes

### 1 — Design System (`src/theme.css` NEW + `src/index.css` MODIFY)

#### [NEW] theme.css
Complete dual-theme design token sheet. Defines `:root[data-theme="dark"]` and `:root[data-theme="light"]` with:

```
Dark theme:
  --bg:           #070B14         (deep space)
  --surface:      #0D1220
  --surface-2:    #131929
  --surface-3:    #1A2236
  --border:       rgba(124,110,250,0.12)
  --border-glow:  rgba(124,110,250,0.35)
  --primary:      #7C6EFA         (electric indigo)
  --primary-rgb:  124,110,250
  --cyan:         #00D4FF
  --emerald:      #00E5B0
  --amber:        #FFB830
  --rose:         #FF6B8A
  --text:         #E8EAF0
  --text-muted:   #8892A4
  --text-dim:     #4A5568
  --aurora-1:     #7C6EFA
  --aurora-2:     #00D4FF
  --aurora-3:     #00E5B0

Light theme:
  --bg:           #FAF8F5         (warm parchment)
  --surface:      #FFFFFF
  --surface-2:    #F5F2EE
  --surface-3:    #EDE9E3
  --border:       rgba(180,160,120,0.2)
  --border-glow:  rgba(204,120,92,0.35)
  --primary:      #CC785C         (terracotta)
  --cyan:         #2E86AB
  --emerald:      #2D6A4F
  --amber:        #C8833B
  --text:         #1A1612
  --text-muted:   #6B5E52
  --text-dim:     #A99080
```

New keyframes added:
- `@keyframes starsTwinkle` — subtle opacity pulse on individual stars
- `@keyframes starsMove` — slow drift on 3 star layers (parallax)
- `@keyframes aurora` — hue-rotate + opacity on aurora bar
- `@keyframes cursorBlink` — terminal cursor
- `@keyframes confettiBurst` — XP celebration stars radiate outward
- `@keyframes mistFloat` — gentle upward drift for orbs

#### [MODIFY] index.css
- Swap `@import` to also load **Playfair Display** from Google Fonts
- Change `--font-display` to `'Playfair Display', Georgia, serif`
- Extend `.heading-xl`, `.heading-lg` to use letter-spacing and improved line-height
- Upgrade `.glass` / `.glass-strong` to use new tokens + stronger blur (32px)
- Upgrade `.btn-primary` shimmer — add `::after` pseudo-element slide-shine on hover
- Upgrade `.sidebar` — add aurora top accent + glass treatment
- Upgrade `.card` — more nuanced border + hover glow instead of just border-color
- Upgrade `.xp-bar-fill` — animated shimmer overlay
- New class `.skill-node` — for roadmap activity nodes with connection lines
- New class `.star-bg` — used by StarField component
- New class `.cursor-trail` — dot trail in dark mode
- New class `.theme-toggle` — stylised toggle pill

---

### 2 — New Components

#### [NEW] `src/hooks/useTheme.js`
```js
// Reads/writes data-theme attribute on <html>
// Persists to localStorage
// Returns { theme, toggleTheme }
```

#### [NEW] `src/components/StarField.jsx`
- Pure CSS star layers (no canvas, no WebGL)
- 3 `<div>` layers: small/medium/large stars
- Each layer has different `animation-duration` (parallax feel)
- Stars generated as `radial-gradient` dots on transparent background
- Only renders in dark mode (reads `data-theme`)
- Absolutely positioned, `pointer-events: none`, `z-index: 0`

#### [NEW] `src/components/ThemeToggle.jsx`
- Beautiful pill toggle: 🌙 ↔ ☀️
- Smooth slide animation
- Placed in Sidebar footer area (above Logout)

#### [NEW] `src/components/AuroraBar.jsx`
- A 4px tall bar at the top of the sidebar
- Slowly shifts through `--aurora-1 → --aurora-2 → --aurora-3`
- Subtle glow blur below

#### [NEW] `src/components/XPBurst.jsx`
- Triggered when `onXPEarned(amount)` is called
- Renders 12 tiny star `span` elements that radiate outward via CSS keyframe
- Auto-removes after 1.2s

---

### 3 — App Shell (`src/App.jsx` MODIFY)

- Wrap entire app in a `ThemeProvider` context (or just use the `useTheme` hook at root level)
- Add `<StarField />` globally (conditionally in dark mode)
- Attach a `useEffect` for cursor trail in dark mode

---

### 4 — Sidebar (`src/components/Sidebar.jsx` MODIFY)

Major visual upgrade:
- Add `<AuroraBar />` at very top
- Logo section: Playfair Display font, "✦ LearnWise" with tiny star prefix
- User avatar: gradient ring, initials styled with serif font
- Nav items: pill shape, icon becomes a mini glyph with glow on active
- Active state: full left-border accent line + glass background
- Language badge: upgraded with flag emoji + animated shimmer
- `<ThemeToggle />` above logout
- Logout row: subtle red glow on hover
- Add smooth `cubic-bezier` transitions on all interactive elements
- Mobile: hamburger menu with slide-in drawer + backdrop blur

---

### 5 — Auth Pages MODIFY

#### LoginPage.jsx + RegisterPage.jsx
- Background: multi-layered `<StarField />` visible behind the glass card (dark mode)
- Light mode: warm paper texture gradient
- Glass card: stronger blur, warmer tint in light mode
- Logo: Playfair Display, animated typing cursor after "LearnWise|"
- Form inputs: floating label style (label animates up when focused)
- Submit button: shimmer sweep on hover + glow
- Social proof line: "Join 1,000+ learners" under logo (static, decorative)
- Split layout on desktop: left = branding/illustration area, right = form (Register only)

---

### 6 — Dashboard (`src/pages/dashboard/DashboardPage.jsx` MODIFY)

Most impactful page — skill tree visual:

- **Month cards**: upgraded — left coloured accent border (activity-type gradient), month number in a styled circle
- **Block rows**: subtle separator line replaced by a dotted path connector (skill tree aesthetic)
- **Activity nodes**: circular instead of rectangular, with:
  - Glow ring in activity colour (completed = full ring, current = pulsing, locked = dim)
  - Icon centered, XP label below
  - Connected by thin SVG lines (static, drawn with CSS borders + absolute positioning)
- **XP bar**: upgraded with shimmering gradient + `0%→X%` count-up animation on load
- **Header**: language flag pair with a large gradient title
- **Loading state**: skeleton shimmer cards instead of plain spinner

---

### 7 — Activity Pages (MODIFY — shared styling only)

The activity pages (`LessonPage`, `VocabPage`, `ReadingPage`, etc.) will get:
- Upgraded page header with activity-type colour accent bar
- Glass card for the content area
- Progress indicator at top (step X of Y dots)
- ScoreModal: redesigned with confetti burst, animated ring, and better button styles

#### [MODIFY] `src/components/ScoreModal.jsx`
- Animated SVG ring draws on mount
- `<XPBurst />` fires when passed
- Better typography — Playfair Display for the big score number
- Pass = emerald glow, Fail = warm amber glow (not harsh red)

---

### 8 — Social Pages (MODIFY)

#### LeaderboardPage.jsx
- Replace table with card-per-row layout
- Top 3 rows: podium styling with badge sizes (🥇 = 1.2x scale, gold bg)
- User's own row: highlighted with primary glow border
- Tab switcher: pill style

#### ProfilePage.jsx
- Hero section: large avatar circle with gradient ring + display name in Playfair
- Stats row: XP total, friends count, pairs started — each in a glass card
- Edit mode: smooth in-place transition

#### SearchFriendsPage.jsx
- Search bar: full-width with magnifying glass icon inside
- Results: user cards with avatar + name + "Add Friend" pulse glow button

---

### 9 — Onboarding (`src/pages/onboarding/OnboardingPage.jsx` MODIFY)

- Language cards: larger, richer — flag in a circle, name in Playfair, description italic
- Selected language: glows with aurora shimmer border
- Step indicator: "Step 1 of 2" dot trail at top
- Arrow between source → target: animated pointing arrow

---

### 10 — HTML Entry (`index.html` MODIFY)

Add Playfair Display + JetBrains Mono to Google Fonts link.

---

## Additional Design Improvements (Suggestions 💡)

> These are strong recommendations that would significantly elevate the product:

1. **Streak counter in Sidebar** — Show a 🔥 flame with day count. Keeps users coming back daily.
2. **Ambient sound toggle 🔇/🔊** — Subtle lo-fi background music during activities (just a button, user-opt-in).
3. **Activity type color legend** in the dashboard header — a small legend strip explaining each color.
4. **Notification bell** in sidebar — even if empty now, the UI affordance builds trust.
5. **Progress ring** on profile avatar in sidebar — a thin SVG circle showing level progress.
6. **Keyboard shortcuts** — `Escape` to close modal, `Enter` to submit, shown as subtle `⌘K` hints.
7. **Scroll progress bar** — thin colored line at top of page (like GitHub/Medium) on long activity pages.
8. **Offline indicator** — a slim banner when the API is unreachable.
9. **Empty state illustrations** — when leaderboard/friends list is empty, show a styled SVG character instead of plain text.
10. **Ripple effect on buttons** — material-style radial ripple on click (CSS only, no library).

---

## Verification Plan

### Build Check
```bash
npm run build   # must produce 0 errors
```

### Dev Preview
```bash
npm run dev     # start dev server and manually verify each page
```

### Manual Verification Checklist
- [ ] Login page: dark mode star field, glass card, typing cursor, form works
- [ ] Register page: split layout, floating labels, form submits correctly
- [ ] Sidebar: aurora bar, theme toggle persists on reload, nav active states
- [ ] Dashboard: skill tree nodes, XP bar animation, month expand/collapse
- [ ] Onboarding: language cards, animated arrow, start button works
- [ ] Leaderboard: podium cards, tab switch
- [ ] Profile: hero avatar, edit mode transition
- [ ] ScoreModal: ring animation, XP burst fires
- [ ] Light mode toggle: all tokens switch, no FOUC
- [ ] Mobile: sidebar drawer works, cards stack
- [ ] No logic regressions: API calls, routing, auth guards unchanged

---

## File Change Summary

| File | Action | Notes |
|---|---|---|
| `index.html` | MODIFY | Add Playfair Display + JetBrains Mono fonts |
| `src/theme.css` | NEW | Dual-theme CSS token system |
| `src/index.css` | MODIFY | Font swap, glass, buttons, animations |
| `src/App.jsx` | MODIFY | Add ThemeProvider, StarField, cursor trail |
| `src/hooks/useTheme.js` | NEW | Theme hook |
| `src/components/StarField.jsx` | NEW | Animated star background |
| `src/components/ThemeToggle.jsx` | NEW | Sun/moon toggle |
| `src/components/AuroraBar.jsx` | NEW | Aurora gradient accent bar |
| `src/components/XPBurst.jsx` | NEW | XP confetti burst |
| `src/components/Sidebar.jsx` | MODIFY | Full visual redesign |
| `src/components/ScoreModal.jsx` | MODIFY | Ring animation, XP burst, new styles |
| `src/pages/auth/LoginPage.jsx` | MODIFY | Star bg, typing cursor, floating labels |
| `src/pages/auth/RegisterPage.jsx` | MODIFY | Split layout, enhanced styling |
| `src/pages/onboarding/OnboardingPage.jsx` | MODIFY | Language card redesign, step indicator |
| `src/pages/dashboard/DashboardPage.jsx` | MODIFY | Skill tree nodes, skeleton loaders |
| `src/pages/social/LeaderboardPage.jsx` | MODIFY | Podium cards, pill tabs |
| `src/pages/social/ProfilePage.jsx` | MODIFY | Hero section, stats cards |
| `src/pages/social/SearchFriendsPage.jsx` | MODIFY | Search bar, user cards |

**Zero changes to:** `src/api/`, `src/store/`, `src/hooks/` (existing), all backend files.

# LearnWise UI Redesign — Task Tracker

## Foundation
- [/] `index.html` — Add Playfair Display + JetBrains Mono fonts
- [ ] `src/theme.css` (NEW) — Dual-theme design tokens + keyframes
- [ ] `src/index.css` (MODIFY) — Font swap, glass, buttons, star-bg, animations

## New Hooks & Components
- [ ] `src/hooks/useTheme.js` (NEW)
- [ ] `src/components/StarField.jsx` (NEW)
- [ ] `src/components/ThemeToggle.jsx` (NEW)
- [ ] `src/components/AuroraBar.jsx` (NEW)
- [ ] `src/components/XPBurst.jsx` (NEW)

## App Shell
- [ ] `src/App.jsx` (MODIFY) — ThemeProvider, StarField, cursor trail

## Core Components
- [ ] `src/components/Sidebar.jsx` (MODIFY) — Full redesign
- [ ] `src/components/ScoreModal.jsx` (MODIFY) — Ring anim, XP burst

## Pages
- [ ] `src/pages/auth/LoginPage.jsx`
- [ ] `src/pages/auth/RegisterPage.jsx`
- [ ] `src/pages/onboarding/OnboardingPage.jsx`
- [ ] `src/pages/dashboard/DashboardPage.jsx`
- [ ] `src/pages/social/LeaderboardPage.jsx`
- [ ] `src/pages/social/ProfilePage.jsx`
- [ ] `src/pages/social/SearchFriendsPage.jsx`

## Verification
- [ ] `npm run build` — 0 errors
- [ ] Manual page-by-page check

it is good but i really dont like purple shades or blue on the website 
it should be dark, black or shades of gray colors.
and light part is too much light it shloid not be that much light.
and also in background change star effect to somthing else.
i dont see any glass finishing ( i want glassy, blur )
and also that cursor tracer i dont like that too, so remvove that and insted make cursor interect with background.
and do some web type of things in background that can be interected ( web but space nebula effects )

there are more changes to make 
1. that background webs should be moveing automatically
2. in dark mode there should be some light border to differentiate from background and same for light mode ( do claude theme that orange color for liht theme border )
3. in quiz and other bolocks there should be glassy effect and also add some more color shades 
4. there should be some changes to make in ui of leaderboard ( make gold color and other colors border and more effects in that side when i hover 
5. remove that flags from login page 

and some more colors ( i like pure bright color with light effect in background of cards )complte pure form with light effect to make website dark and light mode to blend

in activities that circle colors do all this colors 
-- 		red1 = "#c73c3f",
-- 		red = "#f43841",
-- 		red2 = "#ff4f58",
-- 		green = "#73c936",
-- 		yellow = "#ffdd33",
-- 		brown = "#cc8c3c",
-- 		quartz = "#95a99f",
-- 		niagara2 = "#303540",
-- 		niagara1 = "#565f73",
-- 		niagara = "#96a6c8",
-- 		wisteria = "#9e95c7",


and also remove that light effect in that 
just make it glassy.

and also in leaderboard make those cards mattalic.

in leader board that matel flash stays and visible fix that. and also make it faster.
and also in that leader board profile symbol should be in the middle and right bottom side should be madel.
in profile make that block more glassy and blurred.

still there is bug, when i hoever over the any leaderboard place then that metal flash is looping over and also end of the animaton it is not going complete out of frame ( still visible ).
also add crown to the profile at the top.
and still there is no color changes in the activities i wanted complete base form of colors like take example of this red color "#f43841". do that with other colors.

and you accidently deleted intire code base emoji and that cause too many prolbems revert back those changes NOW

