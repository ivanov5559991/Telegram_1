import os
import re
import sys

SETTINGS_PATH   = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
USERCONFIG_PATH = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
MESSAGES_PATH   = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
UI_DIR          = "TMessagesProj/src/main/java/org/telegram/ui"

PREMIUM_ACTIVITY = """\
package org.telegram.ui;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.widget.Toast;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Components.RecyclerListView;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

public class WeryGramPremiumActivity extends BaseFragment {

    private static final int ROW_HEADER            = 0;
    private static final int ROW_VISUAL_PREMIUM    = 1;
    private static final int ROW_VERIFIED_BADGE    = 2;
    private static final int ROW_HIDE_ADS          = 3;
    private static final int ROW_ANIMATED_EMOJI    = 4;
    private static final int ROW_PREMIUM_STICKERS  = 5;
    private static final int ROW_PREMIUM_REACTIONS = 6;
    private static final int ROWS_COUNT            = 7;

    private static final String KEY_VISUAL_PREMIUM  = "visual_premium";
    private static final String KEY_VERIFIED        = "wery_verified";
    private static final String KEY_HIDE_ADS        = "wery_hide_ads";
    private static final String KEY_ANIM_EMOJI      = "wery_anim_emoji";
    private static final String KEY_PREM_STICKERS   = "wery_prem_stickers";
    private static final String KEY_PREM_REACTIONS  = "wery_prem_reactions";

    private RecyclerListView listView;
    private ListAdapter adapter;

    private static android.content.SharedPreferences prefs() {
        return MessagesController.getGlobalMainSettings();
    }
    private static boolean get(String key) { return prefs().getBoolean(key, false); }
    private static void set(String key, boolean v) { prefs().edit().putBoolean(key, v).apply(); }

    @Override
    public boolean onFragmentCreate() {
        super.onFragmentCreate();
        return true;
    }

    @Override
    public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setTitle("WeryGram Premium");
        actionBar.setAllowOverlayTitle(true);
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override
            public void onItemClick(int id) {
                if (id == -1) finishFragment();
            }
        });

        fragmentView = new FrameLayout(context);
        FrameLayout layout = (FrameLayout) fragmentView;
        layout.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundGray));

        listView = new RecyclerListView(context);
        listView.setLayoutManager(new LinearLayoutManager(context, LinearLayoutManager.VERTICAL, false));
        listView.setVerticalScrollBarEnabled(false);
        adapter = new ListAdapter(context);
        listView.setAdapter(adapter);

        listView.setOnItemClickListener(new RecyclerListView.OnItemClickListener() {
            @Override
            public void onItemClick(View view, int position) {
                if (!(view instanceof TextCheckCell)) return;
                TextCheckCell cell = (TextCheckCell) view;
                switch (position) {
                    case ROW_VISUAL_PREMIUM: {
                        boolean next = !get(KEY_VISUAL_PREMIUM);
                        set(KEY_VISUAL_PREMIUM, next);
                        if (next) {
                            set(KEY_VERIFIED, true);
                            set(KEY_ANIM_EMOJI, true);
                            set(KEY_PREM_STICKERS, true);
                            set(KEY_PREM_REACTIONS, true);
                        }
                        cell.setChecked(next);
                        adapter.notifyDataSetChanged();
                        toast(next ? "WeryGram: Premium AKTIVIROVAN!" : "WeryGram: Premium otklyuchen");
                        break;
                    }
                    case ROW_VERIFIED_BADGE: {
                        boolean next = !get(KEY_VERIFIED);
                        set(KEY_VERIFIED, next);
                        cell.setChecked(next);
                        toast(next ? "Galocka vklyuchena" : "Galocka skryta");
                        break;
                    }
                    case ROW_HIDE_ADS: {
                        boolean next = !get(KEY_HIDE_ADS);
                        set(KEY_HIDE_ADS, next);
                        cell.setChecked(next);
                        toast(next ? "Reklama skryta" : "Reklama vklyuchena");
                        break;
                    }
                    case ROW_ANIMATED_EMOJI: {
                        boolean next = !get(KEY_ANIM_EMOJI);
                        set(KEY_ANIM_EMOJI, next);
                        cell.setChecked(next);
                        toast(next ? "Animirovannye emoji vklyucheny" : "Emoji otklucheny");
                        break;
                    }
                    case ROW_PREMIUM_STICKERS: {
                        boolean next = !get(KEY_PREM_STICKERS);
                        set(KEY_PREM_STICKERS, next);
                        cell.setChecked(next);
                        toast(next ? "Premium stikery vklyucheny" : "Stikery otklucheny");
                        break;
                    }
                    case ROW_PREMIUM_REACTIONS: {
                        boolean next = !get(KEY_PREM_REACTIONS);
                        set(KEY_PREM_REACTIONS, next);
                        cell.setChecked(next);
                        toast(next ? "Rasshirennye reaktsii vklyucheny" : "Reaktsii bazovye");
                        break;
                    }
                }
            }
        });

        layout.addView(listView, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT));

        return fragmentView;
    }

    private void toast(String msg) {
        if (getParentActivity() != null)
            Toast.makeText(getParentActivity(), msg, Toast.LENGTH_SHORT).show();
    }

    private class ListAdapter extends RecyclerView.Adapter {
        private static final int TYPE_HEADER = 0;
        private static final int TYPE_CHECK  = 1;
        private final Context mCtx;

        ListAdapter(Context ctx) { mCtx = ctx; }

        @Override public int getItemCount() { return ROWS_COUNT; }
        @Override public int getItemViewType(int pos) { return pos == ROW_HEADER ? TYPE_HEADER : TYPE_CHECK; }

        @Override
        public RecyclerView.ViewHolder onCreateViewHolder(ViewGroup parent, int type) {
            if (type == TYPE_HEADER) {
                TextView tv = new TextView(mCtx);
                tv.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(14),
                    AndroidUtilities.dp(21), AndroidUtilities.dp(6));
                tv.setTextSize(13);
                tv.setTextColor(0xFF79879B);
                tv.setText("VIZUALNYE NASTROYKI");
                tv.setLayoutParams(new RecyclerView.LayoutParams(
                    RecyclerView.LayoutParams.MATCH_PARENT,
                    RecyclerView.LayoutParams.WRAP_CONTENT));
                return new RecyclerView.ViewHolder(tv) {};
            }
            TextCheckCell v = new TextCheckCell(mCtx);
            v.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
            return new RecyclerView.ViewHolder(v) {};
        }

        @Override
        public void onBindViewHolder(RecyclerView.ViewHolder holder, int pos) {
            if (pos == ROW_HEADER) return;
            TextCheckCell cell = (TextCheckCell) holder.itemView;
            switch (pos) {
                case ROW_VISUAL_PREMIUM:
                    cell.setTextAndCheck("Vizualno Telegram Premium", get(KEY_VISUAL_PREMIUM), true); break;
                case ROW_VERIFIED_BADGE:
                    cell.setTextAndCheck("Galocka verifikatsii", get(KEY_VERIFIED), true); break;
                case ROW_HIDE_ADS:
                    cell.setTextAndCheck("Skryt reklamu", get(KEY_HIDE_ADS), true); break;
                case ROW_ANIMATED_EMOJI:
                    cell.setTextAndCheck("Animirovannye emoji", get(KEY_ANIM_EMOJI), true); break;
                case ROW_PREMIUM_STICKERS:
                    cell.setTextAndCheck("Premium stikery", get(KEY_PREM_STICKERS), true); break;
                case ROW_PREMIUM_REACTIONS:
                    cell.setTextAndCheck("Rasshirennye reaktsii", get(KEY_PREM_REACTIONS), true); break;
            }
        }
    }
}
"""


def patch_settings(code):
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)

    BUTTON = ('items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, '
              'R.drawable.msg_settings, "WeryGram Premium"));')

    match = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match:
        anchor = match.group(1)
        code = code.replace(anchor, f'{BUTTON}\n        {anchor}', 1)
        print("OK Knopka WeryGram Premium dobavlena.")
    else:
        code = code.replace("switch (item.id) {", f"{BUTTON}\n        switch (item.id) {{", 1)
        print("OK Knopka dobavlena rezervnym metodom.")

    CLICK = """\
case 9999: {
            presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
            break;
        }"""
    if "switch (item.id) {" in code:
        code = code.replace("switch (item.id) {", f"switch (item.id) {{\n            {CLICK}", 1)
        print("OK Obrabotchik klika dobavlen.")
    return code


def patch_userconfig(code):
    if "visual_premium" in code:
        print("INFO UserConfig uzhe spatcherovan.")
        return code
    anchor = "public TLRPC.User getCurrentUser() {"
    if anchor not in code:
        print("WARN getCurrentUser() ne najden.")
        return code
    injection = """\
public TLRPC.User getCurrentUser() {
        if (currentUser != null &&
                org.telegram.messenger.MessagesController.getGlobalMainSettings()
                    .getBoolean("visual_premium", false)) {
            currentUser.premium  = true;
            currentUser.verified = true;
        }"""
    code = code.replace(anchor, injection, 1)
    print("OK UserConfig spatcherovan.")
    return code


def patch_messages_controller(code):
    if "visual_premium" in code:
        print("INFO MessagesController uzhe spatcherovan.")
        return code
    OLD = (
        "public TLRPC.User getUser(Long id) {\n"
        "        if (id == 0) {\n"
        "            return UserConfig.getInstance(currentAccount).getCurrentUser();\n"
        "        }\n"
        "        return users.get(id);\n"
        "    }"
    )
    NEW = """\
public TLRPC.User getUser(Long id) {
        if (id == 0) {
            return UserConfig.getInstance(currentAccount).getCurrentUser();
        }
        TLRPC.User user = users.get(id);
        if (user != null && id != null &&
                id.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (MessagesController.getGlobalMainSettings()
                    .getBoolean("visual_premium", false)) {
                user.premium  = true;
                user.verified = true;
            }
        }
        return user;
    }"""
    if OLD in code:
        print("OK MessagesController spatcherovan (exact match).")
        return code.replace(OLD, NEW, 1)
    patched = re.sub(
        r'public TLRPC\.User getUser\(Long\s+(\w+)\)\s*\{'
        r'\s*if\s*\(\1\s*==\s*0\)\s*\{'
        r'\s*return\s+UserConfig\.getInstance\(currentAccount\)\.getCurrentUser\(\);\s*\}'
        r'\s*return\s+(\w+)\.get\(\1\);\s*\}',
        r'''public TLRPC.User getUser(Long \1) {
        if (\1 == 0) {
            return UserConfig.getInstance(currentAccount).getCurrentUser();
        }
        TLRPC.User user = \2.get(\1);
        if (user != null && \1 != null &&
                \1.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (MessagesController.getGlobalMainSettings()
                    .getBoolean("visual_premium", false)) {
                user.premium  = true;
                user.verified = true;
            }
        }
        return user;
    }''', code)
    if patched != code:
        print("OK MessagesController spatcherovan (regex).")
    else:
        print("WARN getUser() ne najden — propuskaem.")
    return patched


def run():
    print("WeryGram Premium Patcher v3.0\n")
    if not os.path.exists(SETTINGS_PATH):
        print(f"ERROR: {SETTINGS_PATH} ne najden")
        sys.exit(1)

    with open(SETTINGS_PATH, "r", encoding="utf-8") as f: code = f.read()
    code = patch_settings(code)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f: f.write(code)

    if os.path.exists(USERCONFIG_PATH):
        with open(USERCONFIG_PATH, "r", encoding="utf-8") as f: uc = f.read()
        uc = patch_userconfig(uc)
        with open(USERCONFIG_PATH, "w", encoding="utf-8") as f: f.write(uc)

    if os.path.exists(MESSAGES_PATH):
        with open(MESSAGES_PATH, "r", encoding="utf-8") as f: mc = f.read()
        mc = patch_messages_controller(mc)
        with open(MESSAGES_PATH, "w", encoding="utf-8") as f: f.write(mc)

    MODULE_DIRS = [
        "TMessagesProj/src/main/java/org/telegram/ui",
        "TMessagesProj_App/src/main/java/org/telegram/ui",
        "TMessagesProj_AppHockeyApp/src/main/java/org/telegram/ui",
        "TMessagesProj_AppHuawei/src/main/java/org/telegram/ui",
        "TMessagesProj_AppStandalone/src/main/java/org/telegram/ui",
    ]
    found = set(MODULE_DIRS)
    for root, dirs, _ in os.walk("."):
        norm = root.replace(os.sep, "/").lstrip("./")
        if norm.endswith("org/telegram/ui") and "/src/main/java/" in norm:
            found.add(norm)

    for ui_dir in sorted(found):
        os.makedirs(ui_dir, exist_ok=True)
        out = os.path.join(ui_dir, "WeryGramPremiumActivity.java")
        with open(out, "w", encoding="utf-8") as f:
            f.write(PREMIUM_ACTIVITY)
        print(f"OK WeryGramPremiumActivity.java -> {out}")

    print("\nVSE MODULI USPESHNO MODIFICIROVANY!")


if __name__ == "__main__":
    run()
                                                                  
