#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys

def patch_werygram_core():
    print("WeryGram Premium Patcher v10.0 zapuskaetsya...")

    settings_path   = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    userconfig_path = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
    messages_path   = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"

    if not os.path.exists(settings_path):
        print(f"ERROR: ne najden {settings_path}")
        sys.exit(1)

    # ==========================================
    # 1. SettingsActivity
    # ==========================================
    with open(settings_path, "r", encoding="utf-8") as f:
        code = f.read()

    code = re.sub(r'case 9999:.*?break;\s*}', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)

    btn = 'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.msg_settings, "WeryGram Premium"));'
    match = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match:
        anchor = match.group(1)
        code = code.replace(anchor, f'{btn}\n        {anchor}', 1)
        print("OK knopka dobavlena")
    else:
        code = code.replace("switch (item.id) {",
            f"{btn}\n        switch (item.id) {{", 1)
        print("OK knopka dobavlena rezervnym metodom")

    click = """\
case 9999: {
            presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
            break;
        }"""
    if "switch (item.id) {" in code:
        code = code.replace("switch (item.id) {",
            f"switch (item.id) {{\n            {click}", 1)
        print("OK obrabotchik klika dobavlen")

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(code)

    # ==========================================
    # 2. UserConfig — вставляем ВНУТРЬ synchronized
    # Оригинальный метод:
    #   public TLRPC.User getCurrentUser() {
    #       synchronized (sync) {
    #           return currentUser;
    #       }
    #   }
    # ==========================================
    if os.path.exists(userconfig_path):
        with open(userconfig_path, "r", encoding="utf-8") as f:
            uc = f.read()

        if not uc.strip().startswith("/*") and not uc.strip().startswith("package"):
            print("ERROR: UserConfig.java slomal!")
            sys.exit(1)

        if "visual_premium" not in uc:
            # Точный anchor — строка внутри synchronized
            OLD = "        synchronized (sync) {\n            return currentUser;\n        }\n    }"
            NEW = (
                "        synchronized (sync) {\n"
                "            if (currentUser != null && org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean(\"visual_premium\", false)) {\n"
                "                currentUser.premium = true;\n"
                "            }\n"
                "            return currentUser;\n"
                "        }\n"
                "    }"
            )
            if OLD in uc:
                uc = uc.replace(OLD, NEW, 1)
                with open(userconfig_path, "w", encoding="utf-8") as f:
                    f.write(uc)
                print("OK UserConfig spatcherovan")
            else:
                print("WARN getCurrentUser() ne najden — propuskaem")
        else:
            print("INFO UserConfig uzhe spatcherovan")

    # ==========================================
    # 3. MessagesController
    # ==========================================
    if os.path.exists(messages_path):
        with open(messages_path, "r", encoding="utf-8") as f:
            mc = f.read()

        if "visual_premium" not in mc:
            OLD = (
                "public TLRPC.User getUser(Long id) {\n"
                "        if (id == 0) {\n"
                "            return UserConfig.getInstance(currentAccount).getCurrentUser();\n"
                "        }\n"
                "        return users.get(id);\n"
                "    }"
            )
            NEW = (
                "public TLRPC.User getUser(Long id) {\n"
                "        if (id == 0) {\n"
                "            return UserConfig.getInstance(currentAccount).getCurrentUser();\n"
                "        }\n"
                "        TLRPC.User user = users.get(id);\n"
                "        if (user != null && id != null && id.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {\n"
                "            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean(\"visual_premium\", false)) {\n"
                "                user.premium = true;\n"
                "            }\n"
                "        }\n"
                "        return user;\n"
                "    }"
            )
            if OLD in mc:
                mc = mc.replace(OLD, NEW, 1)
                print("OK MessagesController spatcherovan")
            else:
                print("WARN MessagesController: signatury ne sovpali")
            with open(messages_path, "w", encoding="utf-8") as f:
                f.write(mc)
        else:
            print("INFO MessagesController uzhe spatcherovan")

    # ==========================================
    # 4. WeryGramPremiumActivity.java
    # ==========================================
    activity = """\
package org.telegram.ui;

import android.content.Context;
import android.view.Gravity;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;

public class WeryGramPremiumActivity extends BaseFragment {

    private static final String KEY_VISUAL_PREMIUM = "visual_premium";
    private static final String KEY_VERIFIED       = "wery_verified";
    private static final String KEY_HIDE_ADS       = "wery_hide_ads";
    private static final String KEY_ANIM_EMOJI     = "wery_anim_emoji";
    private static final String KEY_PREM_STICKERS  = "wery_prem_stickers";
    private static final String KEY_PREM_REACTIONS = "wery_prem_reactions";

    private static boolean get(String key) {
        return MessagesController.getGlobalMainSettings().getBoolean(key, false);
    }

    private static void set(String key, boolean v) {
        MessagesController.getGlobalMainSettings().edit().putBoolean(key, v).apply();
    }

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

        FrameLayout root = new FrameLayout(context);
        root.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundGray));
        fragmentView = root;

        ScrollView scroll = new ScrollView(context);
        root.addView(scroll, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT));

        LinearLayout container = new LinearLayout(context);
        container.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(container);

        TextView header = new TextView(context);
        header.setText("VIZUALNYE NASTROYKI");
        header.setTextSize(13);
        header.setTextColor(0xFF79879B);
        header.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(16),
            AndroidUtilities.dp(21), AndroidUtilities.dp(8));
        container.addView(header);

        addRow(context, container, "Vizualno Telegram Premium", KEY_VISUAL_PREMIUM, new Runnable() {
            @Override public void run() {
                set(KEY_VERIFIED, true);
                set(KEY_ANIM_EMOJI, true);
                set(KEY_PREM_STICKERS, true);
                set(KEY_PREM_REACTIONS, true);
            }
        });
        addRow(context, container, "Galocka verifikacii",  KEY_VERIFIED,       null);
        addRow(context, container, "Skryt reklamu",        KEY_HIDE_ADS,       null);
        addRow(context, container, "Animirovannye emoji",  KEY_ANIM_EMOJI,     null);
        addRow(context, container, "Premium stikery",      KEY_PREM_STICKERS,  null);
        addRow(context, container, "Rasshirennye reakcii", KEY_PREM_REACTIONS, null);

        return fragmentView;
    }

    private void addRow(final Context ctx, LinearLayout parent,
                        final String label, final String key,
                        final Runnable onEnable) {
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        row.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(14),
            AndroidUtilities.dp(21), AndroidUtilities.dp(14));

        TextView tv = new TextView(ctx);
        tv.setText(label);
        tv.setTextSize(16);
        tv.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        row.addView(tv, new LinearLayout.LayoutParams(0,
            LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f));

        final Switch sw = new Switch(ctx);
        sw.setChecked(get(key));
        sw.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton btn, boolean checked) {
                set(key, checked);
                if (checked && onEnable != null) onEnable.run();
                if (getParentActivity() != null) {
                    Toast.makeText(getParentActivity(),
                        label + (checked ? ": ON" : ": OFF"),
                        Toast.LENGTH_SHORT).show();
                }
            }
        });
        row.addView(sw);
        parent.addView(row);

        View divider = new View(ctx);
        divider.setBackgroundColor(0xFFE0E0E0);
        LinearLayout.LayoutParams dp = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 1);
        dp.setMarginStart(AndroidUtilities.dp(21));
        parent.addView(divider, dp);
    }
}
"""

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

    for d in sorted(found):
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, "WeryGramPremiumActivity.java")
        with open(out, "w", encoding="utf-8") as f:
            f.write(activity)
        print(f"OK -> {out}")

    print("\nVSE USPESHNO! Zapuskajte sborku.")

if __name__ == "__main__":
    patch_werygram_core()
    
