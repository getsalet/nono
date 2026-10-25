<?php
/**
 * Plugin Name: AFP Agri Language Bridge
 * Description: Author-scoped REST language/source fields for shared-media agriculture translations.
 * Version: 1.0.0
 */
if (!defined('ABSPATH')) exit;
function afp_agri_languages() { return array('fa-IR','ru-RU','ar-IQ','tg-TJ','en-US'); }
function afp_agri_source_id($id) { $source=(int)get_post_meta($id,'_navar_translation_source_id',true); return $source ?: (int)$id; }
function afp_agri_language($id) { $lang=(string)get_post_meta($id,'_navar_translation_language',true); return in_array($lang,afp_agri_languages(),true)?$lang:'fa-IR'; }
function afp_agri_links($id) {
    $source=afp_agri_source_id($id); $links=array();
    if (get_post_status($source)==='publish') $links['fa-IR']=get_permalink($source);
    foreach (array('ru-RU','ar-IQ','tg-TJ','en-US') as $lang) {
        $ids=get_posts(array('post_type'=>'post','post_status'=>'publish','fields'=>'ids','numberposts'=>2,'meta_query'=>array('relation'=>'AND',array('key'=>'_navar_translation_source_id','value'=>(string)$source),array('key'=>'_navar_translation_language','value'=>$lang))));
        if (count($ids)===1) $links[$lang]=get_permalink($ids[0]);
    }
    return $links;
}
add_action('rest_api_init',function(){
    register_rest_field('post','afp_language',array(
        'get_callback'=>function($post){return afp_agri_language($post['id']);},
        'update_callback'=>function($value,$post){
            $id=is_object($post)?$post->ID:$post['id'];
            if (!current_user_can('edit_post',$id)) return new WP_Error('afp_forbidden','Not editable',array('status'=>403));
            if (!in_array($value,afp_agri_languages(),true)) return new WP_Error('afp_language','Unsupported language',array('status'=>400));
            update_post_meta($id,'_navar_translation_language',$value);return true;
        },'schema'=>array('type'=>'string','enum'=>afp_agri_languages(),'context'=>array('view','edit'))));
    register_rest_field('post','afp_source_post_id',array(
        'get_callback'=>function($post){return afp_agri_source_id($post['id']);},
        'update_callback'=>function($value,$post){
            $id=is_object($post)?$post->ID:$post['id'];$source=absint($value);
            if (!current_user_can('edit_post',$id)||!current_user_can('edit_post',$source)) return new WP_Error('afp_forbidden','Source and target must be editable',array('status'=>403));
            if (get_post_type($source)!=='post'||afp_agri_language($source)!=='fa-IR') return new WP_Error('afp_source','Persian post source required',array('status'=>400));
            update_post_meta($id,'_navar_translation_source_id',$source);return true;
        },'schema'=>array('type'=>'integer','minimum'=>1,'context'=>array('view','edit'))));
    register_rest_field('post','afp_translation_links',array('get_callback'=>function($post){return afp_agri_links($post['id']);},'schema'=>array('type'=>'object','context'=>array('view','edit'),'readonly'=>true)));
});
add_filter('language_attributes',function($attributes){
    if (!is_singular('post')) return $attributes;
    $id=get_queried_object_id();if (!get_post_meta($id,'_navar_translation_language',true)) return $attributes;
    $lang=afp_agri_language($id);$dir=in_array($lang,array('fa-IR','ar-IQ'),true)?'rtl':'ltr';
    return 'lang="'.esc_attr($lang).'" dir="'.esc_attr($dir).'"';
},999);
add_action('wp_head',function(){
    if (!is_singular('post')) return;
    $id=get_queried_object_id();if (!get_post_meta($id,'_navar_translation_source_id',true)) return;
    foreach (afp_agri_links($id) as $lang=>$url) echo '<link rel="alternate" hreflang="'.esc_attr($lang).'" href="'.esc_url($url).'" />'."\n";
});
add_action('wp_footer',function(){
    if (!is_singular('post')) return;
    $links=afp_agri_links(get_queried_object_id());if (count($links)<2) return;
    echo '<script id="afp-agri-language-links">(()=>{const links='.wp_json_encode($links,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE).';for(const a of document.querySelectorAll("a[hreflang]")){const u=links[a.getAttribute("hreflang")];if(u)a.href=u;}})();</script>';
},1001);
