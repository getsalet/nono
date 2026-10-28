"""Explicit educational titles; never modifies publication or retry permissions."""
import copy

def instructional_title(row,matrix):
    locality=matrix['localities'][row['locality_ref']]
    label=matrix['angles'][row['angle_ref']]['seo_short_label'].strip()
    crop=locality['crop'];place=locality['place_label']
    title=f'راهنمای {label}؛ {crop} در {place}'
    if len(title)>78:title=f'راهنمای {label}؛ {crop}، {place}'
    if len(title)>78:raise ValueError('Instructional title exceeds 78 characters; editorial label needs review')
    return title

def migrate_pending_titles(matrix,state,protected_keys=()):
    result=copy.deepcopy(matrix)
    protected=set(protected_keys)|set(state.get('held',{}))|{p['key']for p in state.get('published',[])}
    protected.update(x for x in [state.get('current'),(state.get('intent')or{}).get('key')]if x)
    changed=[]
    for row in result['titles']:
        if row['id']in protected:continue
        title=instructional_title(row,result)
        if row['title']==title:continue
        row.setdefault('legacy_planning_title',row['title'])
        row.update(title=title,title_policy_version=2)
        changed.append(row['id'])
    from validate_niloblog_matrix import normalize
    if len({normalize(r['title'])for r in result['titles']})!=len(result['titles']):raise ValueError('Title migration would create duplicates')
    result['generation_title_policy']={'version':2,'purpose':'explicit_instruction_not_reported_local_event','stable_row_ids':True,'preserve_published_held_current_intent_and_existing_items':True,'grants_publication_or_retry_permission':False}
    return result,{'changed_count':len(changed),'changed_keys':changed,'protected_count':len(protected),'publication_enabled':result['publication_enabled']}
