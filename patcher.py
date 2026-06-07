#!/usr/bin/env python3
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "TMessagesProj", "src", "main", "java")

def find_file(name):
    for dp, _, files in os.walk(SRC):
        if name in files:
            return os.path.join(dp, name)
    return None

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f: f.write(t)
    print(f"✔ {os.path.relpath(p, ROOT)}")

def patch_once(path, marker, insertion, before=False):
    text = read(path)
    if insertion.strip() in text:
        print(f"↩ skip {os.path.relpath(path, ROOT)}"); return True
    if marker not in text:
        print(f"✘ MARKER NOT FOUND: {marker!r}", file=sys.stderr); return False
    repl = (insertion + "\n" + marker) if before else (marker + "\n" + insertion)
    write(path, text.replace(marker, repl, 1)); return True

ACTIVITY = '''\
package org.telegram.ui;
import android.content.Context;
import android.widget.LinearLayout;
import android.widget.Switch;
import android.widget.TextView;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.UserConfig;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;
public class WeryGramPremiumActivity extends BaseFragment {
    @Override
    public android.view.View createView(Context context) {
        actionBar.setBackButtonImage(org.telegram.messenger.R.drawable.ic_ab_back);
        actionBar.setTitle("WeryGram");
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override public void onItemClick(int id) { if (id == -1) finishFragment(); }
        });
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        LinearLayout row = new LinearLayout(context);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(AndroidUtilities.dp(16),AndroidUtilities.dp(14),AndroidUtilities.dp(16),AndroidUtilities.dp(14));
        row.setGravity(android.view.Gravity.CENTER_VERTICAL);
        LinearLayout labels = new LinearLayout(context);
        labels.setOrientation(LinearLayout.VERTICAL);
        labels.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        TextView title = new TextView(context);
        title.setText("Visual Premium");
        title.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 16);
        title.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        TextView sub = new TextView(context);
        sub.setText("\u0414\u0430\u0451\u0442 \u0432\u0438\u0437\u0443\u0430\u043b\u044c\u043d\u043e Telegram Premium");
        sub.setTextSize(android.util.TypedValue.COMPLEX_UNIT_SP, 13);
        sub.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteGrayText2));
        labels.addView(title); labels.addView(sub);
        android.view.View div = new android.view.View(context);
        div.setBackgroundColor(Theme.getColor(Theme.key_divider));
        LinearLayout.LayoutParams dp2 = new LinearLayout.LayoutParams(AndroidUtilities.dp(1), AndroidUtilities.dp(40));
        dp2.setMargins(AndroidUtilities.dp(12),0,AndroidUtilities.dp(12),0);
        div.setLayoutParams(dp2);
        Switch toggle = new Switch(context);
        UserConfig cfg = UserConfig.getInstance(currentAccount);
        toggle.setChecked(cfg.werygramVisualPremium);
        toggle.setOnCheckedChangeListener((btn, checked) -> { cfg.werygramVisualPremium = checked; cfg.saveConfig(false); });
        row.addView(labels); row.addView(div); row.addView(toggle);
        root.addView(row);
        fragmentView = root; return fragmentView;
    }
}
'''

def main():
    print("▶ WeryGram patcher\n")
    errors = 0

    uc = find_file("UserConfig.java")
    if not uc: print("✘ UserConfig.java not found", file=sys.stderr); sys.exit(1)

    uc_anchors = ["public boolean registeredForPush;", "public boolean draftsLoaded;", "public boolean contactsReimported;"]
    uc_anchor = next((a for a in uc_anchors if a in read(uc)), None)
    if uc_anchor:
        if not patch_once(uc, uc_anchor, "    public boolean werygramVisualPremium = false;"): errors += 1
    else:
        print("✘ UserConfig: якорь для поля не найден", file=sys.stderr); errors += 1

    save_anchors = ["editor.commit();", "editor.apply();"]
    save_anchor = next((a for a in save_anchors if a in read(uc)), None)
    if save_anchor:
        if not patch_once(uc, save_anchor, '        editor.putBoolean("werygramVisualPremium", werygramVisualPremium);', before=True): errors += 1
    else:
        print("✘ UserConfig: editor.commit/apply не найден", file=sys.stderr); errors += 1

    load_anchors = [
        'registeredForPush = preferences.getBoolean("push_registered", false);',
        'draftsLoaded = preferences.getBoolean(',
        'contactsReimported = preferences.getBoolean(',
    ]
    load_anchor = next((a for a in load_anchors if a in read(uc)), None)
    if load_anchor:
        if not patch_once(uc, load_anchor, '        werygramVisualPremium = preferences.getBoolean("werygramVisualPremium", false);'): errors += 1
    else:
        print("✘ UserConfig: якорь loadConfig не найден", file=sys.stderr); errors += 1

    sa = find_file("SettingsActivity.java")
    if not sa: print("✘ SettingsActivity.java not found", file=sys.stderr); sys.exit(1)

    if not patch_once(sa, "import org.telegram.ui.Components.", "import org.telegram.ui.WeryGramPremiumActivity;", before=True): errors += 1

    fill_anchors = [
        "void fillItems(ArrayList<UItem> items, UniversalAdapter adapter) {",
        "public void fillItems(ArrayList<UItem> items, UniversalAdapter adapter) {",
        "private void fillItems(ArrayList<UItem> items, UniversalAdapter adapter) {",
    ]
    fill_anchor = next((a for a in fill_anchors if a in read(sa)), None)
    if fill_anchor:
        if not patch_once(sa, fill_anchor,
            fill_anchor.replace("{", "{\n        items.add(0, UItem.asButton(1000, R.drawable.msg_settings, \"WeryGram\"));")):
            errors += 1

        click_anchors = [
            "void onItemClick(UItem item, View view, int position, float x, float y) {",
            "public void onItemClick(UItem item, View view, int position, float x, float y) {",
            "private void onItemClick(UItem item, View view, int position, float x, float y) {",
            "private void onClick(UItem item, View view, int position, float x, float y) {",
            "void onClick(UItem item, View view, int position, float x, float y) {",
            "public void onClick(UItem item, View view, int position, float x, float y) {",
            "public boolean onItemClick(int id) {",
            "void onClick(UItem item) {",
            "public void onClick(UItem item) {",
            "onItemClick = (item) -> {",
            "onItemClick = item -> {",
        ]
        click_anchor = next((a for a in click_anchors if a in read(sa)), None)
        if click_anchor:
            if not patch_once(sa, click_anchor,
                click_anchor.replace("{", "{\n        if (item.id == 1000) { presentFragment(new WeryGramPremiumActivity()); return; }")):
                errors += 1
        else:
            print("✘ SettingsActivity: onItemClick не найден", file=sys.stderr); errors += 1
    else:
        print("✘ SettingsActivity: fillItems не найден", file=sys.stderr); errors += 1

    dest = os.path.join(os.path.dirname(sa), "WeryGramPremiumActivity.java")
    if os.path.exists(dest):
        print("↩ skip WeryGramPremiumActivity.java")
    else:
        with open(dest, "w", encoding="utf-8") as f: f.write(ACTIVITY)
        print("✔ created WeryGramPremiumActivity.java")

    if errors > 0:
        print(f"\n✘ {errors} ошибок — сборка остановлена", file=sys.stderr)
        sys.exit(1)
    print("\n✅ Done.")

if __name__ == "__main__":
    main()
