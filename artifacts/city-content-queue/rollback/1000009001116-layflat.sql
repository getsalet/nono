SET NAMES utf8mb4;
USE `navaraby_wp569`;
START TRANSACTION;
SET @rollback_post_id=(SELECT p.ID FROM `ha_posts` p JOIN `ha_postmeta` marker ON marker.post_id=p.ID AND marker.meta_key='_navar_city_queue_generated' AND marker.meta_value='1000009001116-layflat' WHERE p.post_name='نیمور-مرکزی-looleh-nakhi-tashoo' AND p.post_type='arak' LIMIT 1);
DELETE pm FROM `ha_postmeta` pm JOIN `ha_posts` a ON a.ID=pm.post_id WHERE a.post_parent=@rollback_post_id AND a.post_type='attachment';
DELETE FROM `ha_posts` WHERE post_parent=@rollback_post_id AND post_type='attachment';
DELETE FROM `ha_postmeta` WHERE post_id=@rollback_post_id;
DELETE FROM `ha_posts` WHERE ID=@rollback_post_id;
COMMIT;
